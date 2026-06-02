from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.db import get_db, to_json
from services.email_service import send_email, build_feedback_email
from datetime import datetime, timezone
from bson import ObjectId

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/submit", methods=["POST"])
def submit_feedback():
    """Public endpoint — called from website feedback forms."""
    data = request.get_json() or {}
    required = ["name", "email"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    db = get_db()

    domain_key = data.get("domain_key", "")
    domain_doc = db.domains.find_one({"full_key": domain_key}) if domain_key else None

    user_email = None
    site_name  = domain_key or "Website"
    if domain_doc and domain_doc.get("user_id"):
        user = db.users.find_one({"_id": domain_doc["user_id"]})
        if user:
            user_email = user.get("email")
            site_name  = user.get("company") or user.get("name") or site_name

    feedback_doc = {
        "name":      data.get("name", "").strip(),
        "email":     data.get("email", "").strip(),
        "rating":    data.get("rating", ""),
        "feedback":  data.get("feedback", ""),
        "category":  data.get("category", ""),
        "domain_key": domain_key,
        "received_at": datetime.now(timezone.utc),
        "read": False,
        "notification_sent": False,
    }
    result = db.feedback.insert_one(feedback_doc)
    notification_sent = False
    email_errors = []

    # Load SMTP config
    settings_doc = db.settings.find_one({}) or {}
    smtp_cfg = settings_doc.get("smtp") or {}

    if smtp_cfg.get("host") and smtp_cfg.get("from_email"):
        notify_to = user_email or smtp_cfg.get("from_email")
        try:
            template = (settings_doc.get("templates") or {}).get("feedback_email", "")
            if template:
                html_body = template \
                    .replace("{{name}}",     feedback_doc["name"]) \
                    .replace("{{email}}",    feedback_doc["email"]) \
                    .replace("{{rating}}",   str(feedback_doc.get("rating", ""))) \
                    .replace("{{feedback}}", feedback_doc["feedback"]) \
                    .replace("{{category}}", feedback_doc.get("category", "")) \
                    .replace("{{domain}}",   domain_key)
            else:
                html_body = build_feedback_email(feedback_doc, site_name)

            send_email(
                smtp_cfg,
                to=notify_to,
                subject=f"New Feedback from {feedback_doc['name']} — {site_name}",
                html_body=html_body,
            )
            notification_sent = True
        except Exception as e:
            email_errors.append(str(e))
            print(f"Feedback email error: {e}")
    else:
        if not smtp_cfg.get("host"):
            email_errors.append("SMTP not configured — set host in Settings")

    db.feedback.update_one({"_id": result.inserted_id}, {"$set": {"notification_sent": notification_sent}})

    try:
        from routes.notifications import notify_new_feedback
        notify_new_feedback(db, domain_key, feedback_doc["name"], feedback_doc.get("rating"))
    except Exception:
        pass

    response = {
        "message": "Thank you for your feedback! We appreciate your input.",
        "id": str(result.inserted_id),
    }
    if email_errors:
        response["email_warnings"] = email_errors
    return jsonify(response), 201


@feedback_bp.route("/", methods=["GET"])
@jwt_required()
def list_feedback():
    db = get_db()
    feedbacks = list(db.feedback.find().sort("received_at", -1))
    return jsonify([to_json(f) for f in feedbacks]), 200


@feedback_bp.route("/<feedback_id>", methods=["DELETE"])
@jwt_required()
def delete_feedback(feedback_id):
    db = get_db()
    try:
        result = db.feedback.delete_one({"_id": ObjectId(feedback_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Feedback not found"}), 404
        return jsonify({"message": "Deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
