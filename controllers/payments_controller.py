from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from models.payments import Payment
from datetime import datetime

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


# ---------------------------------------------------
# LIST ALL PAYMENT DATES
# ---------------------------------------------------
@payments_bp.route("/")
@login_required
def list_payments():
    """
    Show all distinct dates where payments exist.
    """
    dates = (
        db.session.query(Payment.date)
        .distinct()
        .order_by(Payment.date.desc())
        .all()
    )

    payment_dates = [d[0] for d in dates]

    return render_template(
        "payments/payments_list.html",
        payment_dates=payment_dates
    )


# ---------------------------------------------------
# VIEW PAYMENTS OF SPECIFIC DATE (COMBINED TABLE)
# ---------------------------------------------------
@payments_bp.route("/view/<date>")
@login_required
def payments_by_date(date):

    # Convert URL date string -> Python date
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    except:
        return "Invalid Date Format", 400

    # Fetch all payments of that date
    all_payments = Payment.query.filter_by(date=selected_date).all()

    # Render page with the combined list
    return render_template(
        "payments/payments_view_by_date.html",
        date=selected_date,
        all_payments=all_payments
    )
