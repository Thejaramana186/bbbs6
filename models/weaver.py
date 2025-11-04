from app import db
from datetime import datetime

class Weaver(db.Model):
    __tablename__ = 'weavers'
    
    id = db.Column(db.Integer, primary_key=True)
    weavername = db.Column(db.String(100), nullable=False)
    phonenumber = db.Column(db.String(15), nullable=False)
    aadharcard = db.Column(db.String(200), nullable=True)  # File path for uploaded Aadhaar card
    address = db.Column(db.Text, nullable=True)  # Optional address field
    skills = db.Column(db.Text, nullable=True)  # Optional skills/specialties
    is_active = db.Column(db.Boolean, default=True)  # Active status
    total_credit = db.Column(db.Float, default=0.0)
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Weaver {self.weavername}>'
