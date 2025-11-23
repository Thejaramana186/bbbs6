from app import db
from datetime import date

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    # Payment date
    date = db.Column(db.Date, nullable=False, default=date.today)

    # Payment details
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    # debit / credit
    payment_type = db.Column(db.String(10), nullable=False)

    # Loom and Saree references (optional)
    loom_id = db.Column(db.Integer, nullable=True)
    saree_id = db.Column(db.Integer, nullable=True)

    # handloom / powerloom / outside
    loom_type = db.Column(db.String(50), nullable=True)

    # ---------- OPTIONAL BANK FIELDS ----------
    # If you want account details shown in the new table layout,
    # add these fields in your DB as well.

    account_name = db.Column(db.String(255), nullable=True)
    ifsc_code = db.Column(db.String(50), nullable=True)
    account_no = db.Column(db.String(50), nullable=True)
    account_type = db.Column(db.String(50), nullable=True)
    name_in_bank = db.Column(db.String(120))

    # ------------------------------------------

    def __repr__(self):
        return f"<Payment {self.id} {self.amount} ({self.payment_type})>"
