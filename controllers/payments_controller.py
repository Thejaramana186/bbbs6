from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.payments import Payment
from models.loom import Loom
from models.weaver import Weaver
from datetime import datetime
from sqlalchemy import cast, Date

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


# -------------------------------------------------------------
# ROLE HELPER
# -------------------------------------------------------------
def role():
    return getattr(current_user, "role", "").lower()


# -------------------------------------------------------------
# VIEW PAYMENTS FOR A SPECIFIC DATE
# -------------------------------------------------------------
@payments_bp.route("/view/<date_str>")
@login_required
def payments_by_date(date_str):

    # Convert date from URL
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for("payments.list_payment_dates"))

    # Base query (all payments for that date)
    base_q = (
        Payment.query
        .join(Loom, Payment.loom_id == Loom.id)
        .join(Weaver, Payment.weaver_id == Weaver.id)
        .filter(cast(Payment.date, Date) == selected_date)   # <-- FIXED
    )

    user_role = role()

    # ---------------------------------------------------------
    # ROLE FILTERS
    # ---------------------------------------------------------
    if user_role == "owner":
        pass  # Owner sees everything

    elif user_role in [
        "handloom_factory",
        "powerloom_factory",
        "outside_handloom",
        "outside_powerloom"
    ]:
        base_q = base_q.filter(Loom.user_id == current_user.id)

    else:
        # Weaver sees only his looms
        base_q = base_q.filter(Loom.user_id == current_user.id)

    # ---------------------------------------------------------
    # CATEGORY FILTER FUNCTION
    # ---------------------------------------------------------
    def q(loom_type):
        return base_q.filter(Loom.loom_type == loom_type)

    # ---------------------------------------------------------
    # ROLE-BASED CATEGORY ASSIGNMENT
    # ---------------------------------------------------------
    if user_role == "owner":
        handloom_q = q("Handloom")
        powerloom_q = q("Powerloom")
        outside_handloom_q = q("OutsideHandloom")
        outside_powerloom_q = q("OutsidePowerloom")

    elif user_role == "handloom_factory":
        handloom_q = q("Handloom")
        powerloom_q = outside_handloom_q = outside_powerloom_q = base_q.filter(False)

    elif user_role == "powerloom_factory":
        powerloom_q = q("Powerloom")
        handloom_q = outside_handloom_q = outside_powerloom_q = base_q.filter(False)

    elif user_role == "outside_handloom":
        outside_handloom_q = q("OutsideHandloom")
        handloom_q = powerloom_q = outside_powerloom_q = base_q.filter(False)

    elif user_role == "outside_powerloom":
        outside_powerloom_q = q("OutsidePowerloom")
        handloom_q = powerloom_q = outside_handloom_q = base_q.filter(False)

    else:
        flash("Invalid role. Contact admin.", "danger")
        return redirect(url_for("auth.dashboard"))

    # -------------------------------------------------------------
    # FETCH PAYMENT LISTS
    # -------------------------------------------------------------
    handloom_payments = handloom_q.order_by(Payment.id.desc()).all()
    powerloom_payments = powerloom_q.order_by(Payment.id.desc()).all()
    outside_handloom_payments = outside_handloom_q.order_by(Payment.id.desc()).all()
    outside_powerloom_payments = outside_powerloom_q.order_by(Payment.id.desc()).all()

    # -------------------------------------------------------------
    # TOTALS
    # -------------------------------------------------------------
    def total(rows):
        return float(sum((p.amount or 0) for p in rows))

    totals = {
        "handloom": total(handloom_payments),
        "powerloom": total(powerloom_payments),
        "outside_handloom": total(outside_handloom_payments),
        "outside_powerloom": total(outside_powerloom_payments),
        "grand_total": total(
            handloom_payments +
            powerloom_payments +
            outside_handloom_payments +
            outside_powerloom_payments
        )
    }

    return render_template(
        "payments/payments_view_by_date.html",
        date=selected_date,
        handloom_payments=handloom_payments,
        powerloom_payments=powerloom_payments,
        outside_handloom_payments=outside_handloom_payments,
        outside_powerloom_payments=outside_powerloom_payments,
        totals=totals,
        user_role=user_role
    )


# -------------------------------------------------------------
# LIST OF DATES HAVING PAYMENTS
# -------------------------------------------------------------
@payments_bp.route("/payment-dates")
@login_required
def list_payment_dates():

    user_role = role()

    if user_role == "owner":
        dates = (
            db.session.query(cast(Payment.date, Date).label("d"))   # <-- FIXED
            .distinct()
            .order_by(cast(Payment.date, Date).desc())
            .all()
        )

    else:
        dates = (
            db.session.query(cast(Payment.date, Date).label("d"))   # <-- FIXED
            .join(Loom, Payment.loom_id == Loom.id)
            .filter(Loom.user_id == current_user.id)
            .distinct()
            .order_by(cast(Payment.date, Date).desc())
            .all()
        )

    payment_dates = [d.d for d in dates]  # pick the labeled column

    return render_template(
        "payments/payment_dates.html",
        payment_dates=payment_dates
    )
