from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import traceback

from models.weaver import Weaver
from app import db

weaver_bp = Blueprint('weaver', __name__, url_prefix='/weaver')

# -------------------------------------------------
# Allowed Upload Extensions
# -------------------------------------------------
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------
# AUTO ROLE CHECK: OWNER CAN ACCESS ALL
# -------------------------------------------------
def get_weaver_or_404(weaver_id):
    if getattr(current_user, "role", "").lower() == "owner":
        return Weaver.query.filter_by(id=weaver_id).first_or_404()

    return Weaver.query.filter_by(id=weaver_id, user_id=current_user.id).first_or_404()


# -------------------------------------------------
# LIST WEAVERS
# -------------------------------------------------
@weaver_bp.route('/')
@login_required
def list_weavers():

    if getattr(current_user, "role", "").lower() == "owner":
        weavers = Weaver.query.order_by(Weaver.created_at.desc()).all()
    else:
        weavers = (
            Weaver.query.filter_by(user_id=current_user.id)
            .order_by(Weaver.created_at.desc())
            .all()
        )

    return render_template('weaver.html', weavers=weavers)


# -------------------------------------------------
# CREATE WEAVER
# -------------------------------------------------
@weaver_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_weaver():
    if request.method == 'POST':
        try:
            weavername = request.form.get('weavername')
            phonenumber = request.form.get('phonenumber')

            if not weavername or not phonenumber:
                flash('Weaver name and phone number are required.', 'error')
                return render_template('create_weaver.html')

            address = request.form.get('address', '')
            skills = request.form.get('skills', '')

            # Bank Details
            account_number = request.form.get('account_number')
            ifsc_code = request.form.get('ifsc_code')
            account_type = request.form.get('account_type')
            name_in_bank = request.form.get('name_in_bank')

            # File Upload
            aadharcard_filename = None
            file = request.files.get('aadharcard')

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique = os.urandom(8).hex()
                filename = f"{unique}_{filename}"

                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)

                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                aadharcard_filename = filename

            new_weaver = Weaver(
                weavername=weavername,
                phonenumber=phonenumber,
                address=address,
                skills=skills,
                aadharcard=aadharcard_filename,
                user_id=current_user.id,
                account_number=account_number,
                ifsc_code=ifsc_code,
                account_type=account_type,
                name_in_bank=name_in_bank
            )

            db.session.add(new_weaver)
            db.session.commit()

            flash('Weaver created successfully!', 'success')
            return redirect(url_for('weaver.list_weavers'))

        except Exception as e:
            db.session.rollback()
            print("🔥 create_weaver ERROR:", e)
            traceback.print_exc()
            flash('Error occurred while creating weaver.', 'error')

    return render_template('create_weaver.html')


# -------------------------------------------------
# VIEW WEAVER
# -------------------------------------------------
@weaver_bp.route('/view/<int:id>')
@login_required
def view_weaver(id):
    weaver = get_weaver_or_404(id)
    return render_template('view_weaver.html', weaver=weaver)


# -------------------------------------------------
# EDIT WEAVER
# -------------------------------------------------
@weaver_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_weaver(id):
    weaver = get_weaver_or_404(id)

    if request.method == 'POST':
        try:
            weaver.weavername = request.form.get('weavername')
            weaver.phonenumber = request.form.get('phonenumber')

            if not weaver.weavername or not weaver.phonenumber:
                flash("Weaver name and phone number are required.", "error")
                return render_template("edit_weaver.html", weaver=weaver)

            weaver.address = request.form.get('address', '')
            weaver.skills = request.form.get('skills', '')
            weaver.is_active = 'is_active' in request.form

            # Bank Details
            weaver.account_number = request.form.get('account_number')
            weaver.ifsc_code = request.form.get('ifsc_code')
            weaver.account_type = request.form.get('account_type')
            weaver.name_in_bank = request.form.get('name_in_bank')

            # Aadhaar Upload
            file = request.files.get('aadharcard')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique = os.urandom(8).hex()
                filename = f"{unique}_{filename}"

                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)

                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)

                # Remove previous file
                if weaver.aadharcard:
                    old = os.path.join(upload_folder, weaver.aadharcard)
                    if os.path.exists(old):
                        os.remove(old)

                weaver.aadharcard = filename

            db.session.commit()
            flash('Weaver updated successfully!', 'success')
            return redirect(url_for('weaver.view_weaver', id=weaver.id))

        except Exception as e:
            db.session.rollback()
            print("🔥 edit_weaver ERROR:", e)
            traceback.print_exc()
            flash("Error updating weaver.", "error")

    return render_template('edit_weaver.html', weaver=weaver)


# -------------------------------------------------
# TOGGLE ACTIVE / INACTIVE
# -------------------------------------------------
@weaver_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_status(id):
    weaver = get_weaver_or_404(id)

    try:
        weaver.is_active = not weaver.is_active
        db.session.commit()

        word = "activated" if weaver.is_active else "deactivated"
        flash(f"Weaver {weaver.weavername} has been {word}.", "success")

    except Exception as e:
        db.session.rollback()
        print("🔥 toggle_status ERROR:", e)
        flash("Error updating weaver status.", "error")

    return redirect(url_for('weaver.view_weaver', id=id))


# -------------------------------------------------
# DELETE WEAVER
# -------------------------------------------------
@weaver_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_weaver(id):
    weaver = get_weaver_or_404(id)

    try:
        if weaver.aadharcard:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], weaver.aadharcard)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(weaver)
        db.session.commit()

        flash("Weaver deleted successfully!", "success")

    except Exception as e:
        db.session.rollback()
        print("🔥 delete_weaver ERROR:", e)
        traceback.print_exc()
        flash("Error deleting weaver.", "error")

    return redirect(url_for('weaver.list_weavers'))
