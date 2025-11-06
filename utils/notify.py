from datetime import datetime
from app import db
from models import Notification

def create_notification(user_id, loom_id, message, level="info"):
    """Store a notification in DB"""
    notification = Notification(
        user_id=user_id,
        loom_id=loom_id,
        message=message,
        level=level,
        created_at=datetime.utcnow()
    )
    db.session.add(notification)
    db.session.commit()
