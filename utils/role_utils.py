from flask import abort
from flask_login import current_user

def is_owner():
    return current_user.role == "owner"

def owner_or_403():
    if not is_owner():
        abort(403)
