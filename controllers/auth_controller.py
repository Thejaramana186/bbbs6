from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models.user import User, Activity
from app import db, mail
from datetime import datetime
from flask_mail import Message
import random
import os

auth_bp = Blueprint('auth', __name__)

# ---------------------------------------------------
# EMAIL OTP FUNCTION
# ---------------------------------------------------
def send_otp_email(otp):
    admin_email = os.getenv("OTP_ADMIN_EMAIL")

    if not admin_email:
        raise Exception("OTP_ADMIN_EMAIL is not set!")

    msg = Message(
        subject="BBBS Registration OTP",
        sender=os.getenv("MAIL_USERNAME"),
        recipients=[admin_email]
    )
    msg.body = f"Your BBBS Registration OTP is: {otp}"
    mail.send(msg)
    return True


# ---------------------------------------------------
# HOME
# ---------------------------------------------------
@auth_bp.route('/')
def index():
    return redirect(url_for('auth.dashboard')) if current_user.is_authenticated else redirect(url_for('auth.login'))


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please provide email and password', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user)

            db.session.add(Activity(
                user_id=user.id,
                username=user.username,
                action="login"
            ))
            db.session.commit()

            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('auth.dashboard'))

        flash('Invalid email or password', 'danger')

    return render_template('login.html')


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        role = request.form.get('role')

        if not all([firstname, lastname, username, email, password, confirm, role]):
            flash('All fields are required', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')

        otp = str(random.randint(100000, 999999))

        session['pending_user'] = {
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
        session['reg_otp'] = otp

        send_otp_email(otp)
        flash('OTP sent to admin email', 'info')

        return redirect(url_for('auth.verify_otp'))

    return render_template('register.html')

@auth_bp.route('/activities')
@login_required
def activities():
    if current_user.role != "owner":
        flash("Access denied", "danger")
        return redirect(url_for('auth.dashboard'))

    activities = Activity.query.order_by(Activity.timestamp.desc()).all()
    return render_template(
        "activities.html",
        activities=activities
    )

# ---------------------------------------------------
# OTP VERIFY
# ---------------------------------------------------
@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered = request.form.get('otp')
        stored = session.get('reg_otp')
        data = session.get('pending_user')

        if not entered or not stored or not data:
            flash('Session expired', 'danger')
            return redirect(url_for('auth.register'))

        if entered != stored:
            flash('Invalid OTP', 'danger')
            return render_template('verify_otp.html')

        user = User(
            firstname=data['firstname'],
            lastname=data['lastname'],
            username=data['username'],
            email=data['email'],
            role=data['role']
        )

        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()

        db.session.add(Activity(
            user_id=user.id,
            username=user.username,
            action="register"
        ))
        db.session.commit()

        session.clear()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('verify_otp.html')


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------
@auth_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == "owner":
        users = User.query.all()
        activities = Activity.query.order_by(Activity.timestamp.desc()).limit(5).all()
        return render_template("dashboards/owner_dashboard.html", users=users, recent_activities=activities)

    return render_template(f"dashboards/{current_user.role}_dashboard.html")


# ---------------------------------------------------
# PROFILE
# ---------------------------------------------------
@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


# ---------------------------------------------------
# EDIT PROFILE
# ---------------------------------------------------
@auth_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.firstname = request.form.get('firstname')
        current_user.lastname = request.form.get('lastname')
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')

        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('edit_profile.html')


# ---------------------------------------------------
# CHANGE PASSWORD (LOGIN REQUIRED)
# ---------------------------------------------------
@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not email or not new_password or not confirm_password:
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('auth.change_password'))

        user.set_password(new_password)   # ✅ consistent hashing
        db.session.commit()

        flash('Password updated successfully. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('auth.login'))
