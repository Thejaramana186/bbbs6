from app import db
from datetime import date

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    # Basic fields
    date = db.Column(db.Date, default=date.today, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(10), nullable=False)  # credit / debit

    # Foreign Keys
    loom_id = db.Column(db.Integer, db.ForeignKey('looms.id'), nullable=True)
    saree_id = db.Column(db.Integer, db.ForeignKey('saree_entries.id'), nullable=True)
    weaver_id = db.Column(db.Integer, db.ForeignKey('weavers.id'), nullable=True)

    # Bank Details (Snapshot)
    name_in_bank = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    ifsc_code = db.Column(db.String(50))
    account_type = db.Column(db.String(50))

    # -------------------- Relationships -------------------- #

    # Payment ↔ Loom
    loom_ref = db.relationship(
        "Loom",
        back_populates="payments",
        overlaps="loom,payment_list,payments"
    )

    # Payment ↔ Saree
    saree_entry = db.relationship(
        "SareeEntry",
        back_populates="payments",
        overlaps="saree,saree_ref,payments"
    )

    # Payment ↔ Weaver
    weaver = db.relationship(
        "Weaver",
        back_populates="payments",
        overlaps="weaver_ref,payment_list"
    )

    def __repr__(self):
        return f"<Payment {self.id} {self.amount}>"