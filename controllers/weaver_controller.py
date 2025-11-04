from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from models.weaver import Weaver
from app import db

weaver_bp = Blueprint('weaver', __name__, url_prefix='/weaver')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@weaver_bp.route('/weaver')
@login_required
def weaver():
    weavers = Weaver.query.filter_by(user_id=current_user.id).order_by(Weaver.created_at.desc()).all()
    return render_template('weaver.html', weavers=weavers)

@weaver_bp.route('/create_weaver', methods=['GET', 'POST'])
@login_required
def create_weaver():
    if request.method == 'POST':
        try:
            weavername = request.form.get('weavername')
            phonenumber = request.form.get('phonenumber')
            address = request.form.get('address', '')
            skills = request.form.get('skills', '')
            
            if not weavername or not phonenumber:
                flash('Weaver name and phone number are required', 'error')
                return render_template('create_weaver.html')
            
            # Handle file upload
            aadharcard_path = None
            if 'aadharcard' in request.files:
                file = request.files['aadharcard']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to avoid conflicts
                    timestamp = os.urandom(8).hex()
                    filename = f"{timestamp}_{filename}"
                    
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    aadharcard_path = filename
            
            weaver = Weaver(
                weavername=weavername,
                phonenumber=phonenumber,
                address=address,
                skills=skills,
                aadharcard=aadharcard_path,
                user_id=current_user.id
            )
            
            db.session.add(weaver)
            db.session.commit()
            
            flash('Weaver created successfully!', 'success')
            return redirect(url_for('weaver.weaver'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create weaver. Please try again.', 'error')
    
    return render_template('create_weaver.html')

@weaver_bp.route('/view_weaver/<int:id>')
@login_required
def view_weaver(id):
    weaver = Weaver.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    # No Looms, just send weaver
    return render_template('view_weaver.html', weaver=weaver)

@weaver_bp.route('/edit_weaver/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_weaver(id):
    weaver = Weaver.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            weaver.weavername = request.form.get('weavername')
            weaver.phonenumber = request.form.get('phonenumber')
            weaver.address = request.form.get('address', '')
            weaver.skills = request.form.get('skills', '')
            
            # Update active status
            weaver.is_active = 'is_active' in request.form
            
            if not weaver.weavername or not weaver.phonenumber:
                flash('Weaver name and phone number are required', 'error')
                return render_template('edit_weaver.html', weaver=weaver)
            
            # Handle file upload
            if 'aadharcard' in request.files:
                file = request.files['aadharcard']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to avoid conflicts
                    timestamp = os.urandom(8).hex()
                    filename = f"{timestamp}_{filename}"
                    
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    weaver.aadharcard = filename
            
            db.session.commit()
            flash('Weaver updated successfully!', 'success')
            return redirect(url_for('weaver.view_weaver', id=weaver.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update weaver. Please try again.', 'error')
    
    return render_template('edit_weaver.html', weaver=weaver)

@weaver_bp.route('/toggle_status/<int:id>', methods=['POST'])
@login_required
def toggle_status(id):
    weaver = Weaver.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        weaver.is_active = not weaver.is_active
        db.session.commit()
        status = 'activated' if weaver.is_active else 'deactivated'
        flash(f'Weaver {weaver.weavername} has been {status}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update weaver status. Please try again.', 'error')
    
    return redirect(url_for('weaver.view_weaver', id=weaver.id))

@weaver_bp.route('/delete_weaver/<int:id>', methods=['POST'])
@login_required
def delete_weaver(id):
    weaver = Weaver.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        # Delete associated aadhar file if exists
        if weaver.aadharcard:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], weaver.aadharcard)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(weaver)
        db.session.commit()
        flash('Weaver deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete weaver. Please try again.', 'error')
    
    return redirect(url_for('weaver.weaver'))
