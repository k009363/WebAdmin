from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.db import get_db, to_json
from services.email_service import send_email, build_contact_email, build_auto_reply_email, build_feedback_email
from bson import ObjectId
from datetime import datetime, timezone

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/submit", methods=["POST"])
def submit_contact():
    """Public endpoint — called from website contact forms."""
    data = request.get_json() or {}
    required = ["name", "email", "message"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    db = get_db()

    # Find domain record to get user email
    domain_key = data.get("domain_key", "")
    domain_doc = db.domains.find_one({"full_key": domain_key}) if domain_key else None

    # Resolve user email for notification
    user_email = None
    site_name = domain_key or "Website"
    if domain_doc and domain_doc.get("user_id"):
        user = db.users.find_one({"_id": domain_doc["user_id"]})
        if user:
            user_email = user.get("email")
            site_name = user.get("company") or user.get("name") or site_name

    # Save contact to DB
    contact_doc = {
        "domain_key": domain_key,
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "subject": data.get("subject", "Contact Form"),
        "message": data.get("message", ""),
        "created_at": datetime.now(timezone.utc),
        "notification_sent": False,
    }
    result = db.contacts.insert_one(contact_doc)
    contact_id = result.inserted_id

    # Send emails via stored SMTP settings
    settings_doc = db.settings.find_one({})
    smtp_cfg = (settings_doc or {}).get("smtp")
    notification_sent = False

    email_errors = []
    if smtp_cfg and smtp_cfg.get("host") and smtp_cfg.get("from_email"):
        try:
            # Notify the site owner / linked user
            notify_to = user_email or smtp_cfg.get("from_email")
            if notify_to:
                # Load email template from settings
                template = (settings_doc or {}).get("templates", {}).get("contact_email", "")
                if template:
                    # Replace variables in template
                    html_body = template.replace("{{name}}", contact_doc.get('name', ''))
                    html_body = html_body.replace("{{email}}", contact_doc.get('email', ''))
                    html_body = html_body.replace("{{phone}}", contact_doc.get('phone', ''))
                    html_body = html_body.replace("{{message}}", contact_doc.get('message', ''))
                    html_body = html_body.replace("{{subject}}", contact_doc.get('subject', ''))
                    html_body = html_body.replace("{{domain}}", contact_doc.get('domain_key', ''))
                else:
                    html_body = build_contact_email(contact_doc, site_name)

                send_email(
                    smtp_cfg,
                    to=notify_to,
                    subject=f"New Contact: {data.get('subject','Form Submission')} — {site_name}",
                    html_body=html_body,
                )
                notification_sent = True
        except Exception as e:
            email_errors.append(f"Owner notification: {e}")

        try:
            # Auto-reply to the submitter
            send_email(
                smtp_cfg,
                to=data["email"],
                subject=f"Thank you for contacting {site_name}",
                html_body=build_auto_reply_email(contact_doc, site_name),
            )
        except Exception as e:
            email_errors.append(f"Auto-reply: {e}")

    # Update contact with notification status
    db.contacts.update_one({"_id": contact_id}, {"$set": {"notification_sent": notification_sent}})

    try:
        from routes.notifications import notify_new_contact
        notify_new_contact(db, domain_key, contact_doc["name"], contact_doc["email"])
    except Exception:
        pass

    response = {"message": "Your message has been received. We will be in touch soon!"}
    if email_errors:
        response["email_warnings"] = email_errors
    return jsonify(response), 200


@contact_bp.route("/", methods=["GET"])
@jwt_required()
def list_contacts():
    db = get_db()
    domain_key = request.args.get("domain_key")
    query = {"domain_key": domain_key} if domain_key else {}
    contacts = list(db.contacts.find(query).sort("created_at", -1).limit(200))
    return jsonify(to_json(contacts)), 200


@contact_bp.route("/<contact_id>", methods=["DELETE"])
@jwt_required()
def delete_contact(contact_id):
    db = get_db()
    db.contacts.delete_one({"_id": ObjectId(contact_id)})
    return jsonify({"message": "Deleted"}), 200
