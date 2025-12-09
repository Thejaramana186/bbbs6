from flask import render_template
from flask_login import login_required, current_user
from app.models.weaver import Weaver
from app.models.loom import Loom
from app.models.payments import Payment


@login_required
def dashboard():
    """
    Owner = sees everything  
    Other users = see only their looms, payments, and weavers
    """

    # -----------------------------------------------------
    # OWNER → FULL ACCESS
    # -----------------------------------------------------
    if current_user.role == "owner":

        weavers_count = Weaver.query.count()
        payments_count = Payment.query.count()

        handlooms_count = Loom.query.filter_by(loom_type="handloom_factory").count()
        powerlooms_count = Loom.query.filter_by(loom_type="powerloom_factory").count()
        outside_looms_count = Loom.query.filter_by(loom_type="outside_handloom").count()
        outside_powerlooms_count = Loom.query.filter_by(loom_type="outside_powerloom").count()

    # -----------------------------------------------------
    # NORMAL USER → RESTRICTED ACCESS
    # -----------------------------------------------------
    else:
        weavers_count = Weaver.query.filter_by(user_id=current_user.id).count()

        payments_count = (
            Payment.query.join(Loom, Payment.loom_id == Loom.id)
            .filter(Loom.user_id == current_user.id)
            .count()
        )

        handlooms_count = Loom.query.filter_by(
            user_id=current_user.id, 
            loom_type="handloom_factory"
        ).count()

        powerlooms_count = Loom.query.filter_by(
            user_id=current_user.id, 
            loom_type="powerloom_factory"
        ).count()

        outside_looms_count = Loom.query.filter_by(
            user_id=current_user.id, 
            loom_type="outside_handloom"
        ).count()

        outside_powerlooms_count = Loom.query.filter_by(
            user_id=current_user.id, 
            loom_type="outside_powerloom"
        ).count()

    # -----------------------------------------------------
    return render_template(
        "owner_dashboard.html",
        weavers_count=weavers_count,
        payments_count=payments_count,
        handlooms_count=handlooms_count,
        powerlooms_count=powerlooms_count,
        outside_looms_count=outside_looms_count,
        outside_powerlooms_count=outside_powerlooms_count,
    )
