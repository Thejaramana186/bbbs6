from app import db
from datetime import datetime

class Weaver(db.Model):
    __tablename__ = 'weavers'

    id = db.Column(db.Integer, primary_key=True)
    weavername = db.Column(db.String(100), nullable=False)
    phonenumber = db.Column(db.String(15), nullable=False)

    # Bank fields
    account_number = db.Column(db.String(30), nullable=True)
    ifsc_code = db.Column(db.String(20), nullable=True)
    account_type = db.Column(db.String(20), nullable=True)
    name_in_bank = db.Column(db.String(100), nullable=True)

    aadharcard = db.Column(db.String(200), nullable=True)
    address = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    total_credit = db.Column(db.Float, default=0.0)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Weaver → Loom (One-to-Many)
    looms = db.relationship(
        "Loom",
        backref="weaver",
        lazy=True
    )

    # Weaver → Payments (One-to-Many)
    payments = db.relationship(
        "Payment",
        back_populates="weaver",
        lazy=True,
        overlaps="weaver_ref,payment_list"
    )

    def __repr__(self):
        return f"<Weaver {self.weavername}>"
