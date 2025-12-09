from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
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
        raise Exception("OTP_ADMIN_EMAIL is not set in environment variables!")

    msg = Message(
        subject="BBBS Registration OTP",
        sender=os.getenv("MAIL_USERNAME"),
        recipients=[admin_email]
    )
    msg.body = f"Your BBBS Registration OTP is: {otp}"
    mail.send(msg)
    return True


# ---------------------------------------------------
# HOME / INDEX
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
            flash('Please provide both email and password', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user)

            db.session.add(Activity(user_id=user.id, username=user.username, action="login"))
            db.session.commit()

            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('auth.dashboard'))

        flash('Invalid email or password', 'error')

    return render_template('login.html')


# ---------------------------------------------------
# REGISTER (STEP 1 → SAVE DATA + SEND OTP)
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
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')

        if not all([firstname, lastname, username, email, password, confirm_password, role]):
            flash('All fields are required', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
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

        try:
            send_otp_email(otp)
            flash("OTP has been sent to admin email!", "info")
        except Exception as e:
            flash(f"OTP sending failed: {e}", "error")
            return render_template('register.html')

        return redirect(url_for('auth.verify_otp'))

    return render_template('register.html')


# ---------------------------------------------------
# OTP VERIFICATION
# ---------------------------------------------------
@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        correct_otp = session.get('reg_otp')
        user_data = session.get('pending_user')

        if not entered_otp or not correct_otp:
            flash("Session expired. Please register again.", "error")
            return redirect(url_for('auth.register'))

        if entered_otp != correct_otp:
            flash("Invalid OTP! Please try again.", "error")
            return render_template("verify_otp.html")

        try:
            user = User(
                firstname=user_data["firstname"],
                lastname=user_data["lastname"],
                username=user_data["username"],
                email=user_data["email"],
                role=user_data["role"]
            )

            user.set_password(user_data["password"])
            db.session.add(user)
            db.session.commit()

            db.session.add(Activity(user_id=user.id, username=user.username, action="register"))
            db.session.commit()

            session.pop("reg_otp")
            session.pop("pending_user")

            flash("Registration successful! You can now login.", "success")
            return redirect(url_for('auth.login'))

        except Exception:
            db.session.rollback()
            flash("Registration failed. Try again.", "error")

    return render_template("verify_otp.html")


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------
@auth_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == "owner":
        users = User.query.order_by(User.created_at.desc()).all()
        recent_activities = Activity.query.order_by(Activity.timestamp.desc()).limit(5).all()
        return render_template("dashboards/owner_dashboard.html", users=users, recent_activities=recent_activities)

    if current_user.role == "handloom_factory":
        return render_template("dashboards/handloom_factory_dashboard.html")
    if current_user.role == "outside_handloom":
        return render_template("dashboards/outside_handloom_dashboard.html")
    if current_user.role == "powerloom_factory":
        return render_template("dashboards/powerloom_factory_dashboard.html")
    if current_user.role == "outside_powerloom":
        return render_template("dashboards/outside_powerloom_dashboard.html")

    return "Invalid role assigned. Contact admin.", 403


# ---------------------------------------------------
# ACTIVITIES
# ---------------------------------------------------
@auth_bp.route('/activities')
@login_required
def activities():
    if current_user.role != "owner":
        return "Unauthorized", 403

    logs = Activity.query.order_by(Activity.timestamp.desc()).all()
    return render_template("dashboards/activities.html", activities=logs)


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
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')

        if not all([firstname, lastname, username, email]):
            flash('All fields are required', 'error')
            return render_template('edit_profile.html')

        if User.query.filter(User.username == username, User.id != current_user.id).first():
            flash('Username already exists', 'error')
            return render_template('edit_profile.html')

        if User.query.filter(User.email == email, User.id != current_user.id).first():
            flash('Email already exists', 'error')
            return render_template('edit_profile.html')

        try:
            current_user.firstname = firstname
            current_user.lastname = lastname
            current_user.username = username
            current_user.email = email
            db.session.commit()

            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        except:
            db.session.rollback()
            flash('Profile update failed', 'error')

    return render_template('edit_profile.html')


# ---------------------------------------------------
# CHANGE PASSWORD
# ---------------------------------------------------
@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('change_password.html')

        if not current_user.check_password(current_password):
            flash('Current password incorrect', 'error')
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html')

        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('change_password.html')

        try:
            current_user.set_password(new_password)
            db.session.commit()

            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        except:
            db.session.rollback()
            flash('Password change failed', 'error')

    return render_template('change_password.html')


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('auth.login'))
