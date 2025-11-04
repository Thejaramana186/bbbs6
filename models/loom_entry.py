from app import db
from datetime import date


class Weaver(db.Model):
    __tablename__ = 'weaver'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # A weaver can have multiple looms
    looms = db.relationship('Loom', backref='weaver', lazy=True)

    def __repr__(self):
        return f"<Weaver {self.name}>"


class Loom(db.Model):
    __tablename__ = 'loom'
    id = db.Column(db.Integer, primary_key=True)
    loom_number = db.Column(db.String(50), nullable=False)
    weaver_id = db.Column(db.Integer, db.ForeignKey('weaver.id'), nullable=False)

    # A loom can have multiple entries
    entries = db.relationship('LoomEntry', backref='loom', lazy=True)

    def __repr__(self):
        return f"<Loom {self.loom_number} for Weaver ID {self.weaver_id}>"


class LoomEntry(db.Model):
    __tablename__ = 'loom_entry'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    fabric_name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200))  # For uploaded fabric image
    color = db.Column(db.String(50))
    warp_weft = db.Column(db.String(50))  # Work/cloth type
    material = db.Column(db.String(100))
    amount_credit = db.Column(db.Float, default=0.0)
    amount_debit = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)

    loom_id = db.Column(db.Integer, db.ForeignKey('loom.id'), nullable=False)

    def __repr__(self):
        return f"<LoomEntry {self.fabric_name} on {self.date}>"
