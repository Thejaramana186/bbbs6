from flask import Blueprint, jsonify
from app import db
from models.loom import Loom

notification_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

@notification_bp.route("/", methods=["GET"])
def get_notifications():
    """
    Returns notification messages when only 2 sarees are left for a loom.
    """
    try:
        looms = Loom.query.all()
        notifications = []

        for loom in looms:
            total_sarees = loom.num_sarees or 0

            # Force load saree entries
            added_sarees = len(loom.saree_entries) if loom.saree_entries else 0

            remaining = total_sarees - added_sarees

            # Trigger only when exactly 2 sarees are remaining
            if remaining == 2:
                notifications.append({
                    "loom_id": loom.id,
                    "loom_no": loom.loom_no,
                    "message": f"Loom {loom.loom_no} needs a new warp — only {remaining} sarees remaining!"
                })

        return jsonify({
            "count": len(notifications),
            "notifications": notifications
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
