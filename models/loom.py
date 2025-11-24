from app import db
from datetime import datetime, date
import webcolors

# --------------------------------------------------------
# LOOM MODEL
# --------------------------------------------------------
class Loom(db.Model):
    __tablename__ = 'looms'

    id = db.Column(db.Integer, primary_key=True)
    loom_no = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=True, default=date.today, index=True)

    # ---------------- Relationships ---------------- #
    warps = db.relationship('Warp', back_populates='loom', cascade="all, delete-orphan")
    wefts = db.relationship('Weft', back_populates='loom', cascade="all, delete-orphan")
    colors = db.relationship('WarpColor', back_populates='loom', cascade="all, delete-orphan")

    # ⭐ Correct WeftColor relationship (bidirectional)
    weft_colors = db.relationship(
        'WeftColor',
        back_populates='loom',
        cascade="all, delete-orphan"
    )

    saree_entries = db.relationship(
        'SareeEntry',
        back_populates='loom',
        lazy=True,
        cascade='all, delete-orphan'
    )

    payments = db.relationship(
        "Payment",
        back_populates="loom_ref",
        cascade="all, delete-orphan",
        overlaps="loom,payment_list,payments"
    )

    # Weaver info
    weaver_id = db.Column(db.Integer, db.ForeignKey('weavers.id'), nullable=True)

    # Loom info
    loom_type = db.Column(db.String(50), nullable=False)
    num_sarees = db.Column(db.Integer, nullable=False, default=0)
    saree_type = db.Column(db.String(50), nullable=True)
    saree_name = db.Column(db.String(100), nullable=True)

    # Financials
    amount_credit = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)
    amount_debit = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)

    # User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def balance(self):
        return float(self.amount_credit or 0) - float(self.amount_debit or 0)

    @property
    def remaining_sarees(self):
        try:
            return max(self.num_sarees - len(self.saree_entries), 0)
        except Exception:
            return 0

    def __repr__(self):
        return f"<Loom No: {self.loom_no} ({self.loom_type})>"


# --------------------------------------------------------
# SAREE ENTRY MODEL
# --------------------------------------------------------
class SareeEntry(db.Model):
    __tablename__ = 'saree_entries'

    id = db.Column(db.Integer, primary_key=True)
    saree_number = db.Column(db.Integer, nullable=True)
    saree_name = db.Column(db.String(100), nullable=True)
    saree_image = db.Column(db.String(200), nullable=True)
    colors = db.Column(db.String(200), nullable=True)
    warp_weft = db.Column(db.String(100), nullable=True)
    material = db.Column(db.String(100), nullable=True)
    remarks = db.Column(db.Text, nullable=True)

    border_color = db.Column(db.String(100), nullable=True)
    border_hex = db.Column(db.String(10), nullable=True)
    body_color = db.Column(db.String(100), nullable=True)
    body_hex = db.Column(db.String(10), nullable=True)

    meena_a = db.Column(db.String(100), nullable=True)
    meena_a_hex = db.Column(db.String(10), nullable=True)
    meena_b = db.Column(db.String(100), nullable=True)
    meena_b_hex = db.Column(db.String(10), nullable=True)
    meena_c = db.Column(db.String(100), nullable=True)
    meena_c_hex = db.Column(db.String(10), nullable=True)
    meena_d = db.Column(db.String(100), nullable=True)
    meena_d_hex = db.Column(db.String(10), nullable=True)

    amount_credit = db.Column(db.Numeric(10, 2), default=0.00)
    amount_debit = db.Column(db.Numeric(10, 2), default=0.00)
    date = db.Column(db.Date, nullable=True, default=date.today)
    completion_date = db.Column(db.Date, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    quality_rating = db.Column(db.Integer, nullable=True)

    loom_id = db.Column(db.Integer, db.ForeignKey('looms.id'), nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payments = db.relationship(
        "Payment",
        back_populates="saree_entry",
        cascade="all, delete-orphan",
        overlaps="saree_ref,payments"
    )

    loom = db.relationship("Loom", back_populates="saree_entries")

    @property
    def balance(self):
        return float(self.amount_credit or 0) - float(self.amount_debit or 0)

    @property
    def display_color(self):
        if not self.colors:
            return None

        color_str = self.colors.strip()

        if color_str.upper().endswith("M"):
            return color_str.upper()

        if not any(c in color_str for c in [",", "#"]):
            return color_str.capitalize()

        if color_str.startswith("#"):
            try:
                return webcolors.hex_to_name(color_str)
            except ValueError:
                rgb = webcolors.hex_to_rgb(color_str)
                return self._closest_color_name(rgb)

        if "," in color_str:
            try:
                r, g, b = [int(x.strip()) for x in color_str.split(",")]
                return self._closest_color_name((r, g, b))
            except Exception:
                return color_str

        return color_str

    def _closest_color_name(self, rgb):
        min_colors = {}
        for hex_val, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r, g, b = webcolors.hex_to_rgb(hex_val)
            dist = (r - rgb[0])**2 + (g - rgb[1])**2 + (b - rgb[2])**2
            min_colors[dist] = name
        return min_colors[min(min_colors.keys())]

    def __repr__(self):
        return f"<SareeEntry {self.saree_number}>"


# --------------------------------------------------------
# WARP MODEL
# --------------------------------------------------------
class Warp(db.Model):
    __tablename__ = 'warps'

    id = db.Column(db.Integer, primary_key=True)
    loom_id = db.Column(db.Integer, db.ForeignKey('looms.id'), nullable=False)

    zari_border_left = db.Column(db.String(100))
    zari_border_right = db.Column(db.String(100))
    zari_body = db.Column(db.String(100))
    silk_border_left = db.Column(db.String(100))
    silk_border_right = db.Column(db.String(100))
    silk_body = db.Column(db.String(100))

    loom = db.relationship('Loom', back_populates='warps')

    def __repr__(self):
        return f"<Warp {self.id}>"


# --------------------------------------------------------
# WEFT MODEL
# --------------------------------------------------------
class Weft(db.Model):
    __tablename__ = 'wefts'

    id = db.Column(db.Integer, primary_key=True)
    loom_id = db.Column(db.Integer, db.ForeignKey('looms.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    zari = db.Column(db.String(100))
    silk = db.Column(db.String(100))

    loom = db.relationship('Loom', back_populates='wefts')

    def __repr__(self):
        return f"<Weft {self.id}>"


# --------------------------------------------------------
# WARP COLOR MODEL
# --------------------------------------------------------
class WarpColor(db.Model):
    __tablename__ = 'warp_colors'

    id = db.Column(db.Integer, primary_key=True)
    loom_id = db.Column(db.Integer, db.ForeignKey('looms.id'), nullable=False)
    border_color = db.Column(db.String(100))
    body_color = db.Column(db.String(100))

    loom = db.relationship('Loom', back_populates='colors')

    def __repr__(self):
        return f"<WarpColor {self.id}>"


# --------------------------------------------------------
# ⭐ WEFT COLOR MODEL
# --------------------------------------------------------
class WeftColor(db.Model):
    __tablename__ = 'weft_colors'

    id = db.Column(db.Integer, primary_key=True)
    loom_id = db.Column(db.Integer, db.ForeignKey('looms.id'), nullable=False)

    no_of_sarees = db.Column(db.Integer, nullable=False)
    border_weft = db.Column(db.String(100), nullable=False)
    body_weft = db.Column(db.String(100), nullable=False)

    meena_a = db.Column(db.String(100))
    meena_b = db.Column(db.String(100))
    meena_c = db.Column(db.String(100))
    meena_d = db.Column(db.String(100))

    # ⭐ Critical for query + display
    loom = db.relationship(
        'Loom',
        back_populates='weft_colors'
    )

    def __repr__(self):
        return f"<WeftColor {self.id} for Loom {self.loom_id}>"
