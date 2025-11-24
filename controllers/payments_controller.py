from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.payments import Payment
from datetime import datetime

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


# ======================================================
# 1. LIST ALL PAYMENT DATES (GROUPED BY DATE)
# ======================================================
@payments_bp.route("/")
@login_required
def list_payment_dates():
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


# ======================================================
# 2. VIEW ALL PAYMENTS OF A SPECIFIC DATE
# ======================================================
@payments_bp.route("/view/<date_str>")
@login_required
def payments_by_date(date_str):
    """
    Display all payments on a specific date.
    """

    # Convert URL date string → Python date
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for("payments.list_payment_dates"))

    # Fetch all payments for this date
    all_payments = (
        Payment.query
        .filter_by(date=selected_date)
        .order_by(Payment.id.desc())
        .all()
    )

    return render_template(
        "payments/payments_view_by_date.html",
        date=selected_date,
        all_payments=all_payments
    )
