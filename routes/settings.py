from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.db import get_db, to_json
from datetime import datetime, timezone
from middleware.rbac import jwt_required_with_role
import smtplib

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/", methods=["GET"])
@jwt_required()
def get_settings():
    db = get_db()
    doc = db.settings.find_one({})
    if not doc:
        return jsonify({}), 200
    # Never expose password in GET
    result = to_json(doc)
    if "smtp" in result and "password" in result["smtp"]:
        result["smtp"]["password"] = "••••••••"
    if "cloudinary" in result and "api_secret" in result["cloudinary"]:
        result["cloudinary"]["api_secret"] = "••••••••"
    return jsonify(result), 200


@settings_bp.route("/", methods=["PUT"])
@jwt_required()
def save_settings():
    data = request.get_json() or {}
    db = get_db()
    existing = db.settings.find_one({}) or {}

    update = {"updated_at": datetime.now(timezone.utc)}

    if "smtp" in data:
        smtp = data["smtp"]
        # Keep existing password if placeholder sent
        if smtp.get("password") == "••••••••":
            smtp["password"] = (existing.get("smtp") or {}).get("password", "")
        update["smtp"] = smtp

    if "cloudinary" in data:
        cloud = data["cloudinary"]
        if cloud.get("api_secret") == "••••••••":
            cloud["api_secret"] = (existing.get("cloudinary") or {}).get("api_secret", "")
        update["cloudinary"] = cloud

    if "templates" in data:
        update["templates"] = data["templates"]

    if db.settings.count_documents({}) == 0:
        db.settings.insert_one(update)
    else:
        db.settings.update_one({}, {"$set": update})

    return jsonify({"message": "Settings saved"}), 200


@settings_bp.route("/test-smtp", methods=["POST"])
@jwt_required()
def test_smtp():
    try:
        data  = request.get_json() or {}
        smtp  = data.get("smtp", {})
        to_email = data.get("to_email", smtp.get("from_email", ""))

        if not smtp.get("host"):
            return jsonify({"error": "SMTP host is not set"}), 400
        if not smtp.get("from_email"):
            return jsonify({"error": "From email is not set"}), 400
        if not to_email:
            return jsonify({"error": "No recipient email provided"}), 400

        # Resolve placeholder password from DB
        if smtp.get("password") == "••••••••":
            db = get_db()
            existing = db.settings.find_one({}) or {}
            smtp["password"] = (existing.get("smtp") or {}).get("password", "")

        from services.email_service import send_email
        send_email(
            smtp_cfg=smtp,
            to=to_email,
            subject="SMTP Test — Dynamic Websites Admin",
            html_body="""
            <div style='font-family:Arial;max-width:600px;margin:0 auto;padding:20px;border:1px solid #e5e7eb;border-radius:8px;'>
              <h2 style='color:#4f46e5;'>SMTP Test Successful</h2>
              <p>Your SMTP configuration is working correctly.</p>
              <p style='color:#6b7280;font-size:13px;margin-top:16px;'>Sent from Dynamic Websites Admin Panel</p>
            </div>""",
        )
        return jsonify({"message": f"Test email sent successfully to {to_email}"}), 200

    except Exception as e:
        print(f"SMTP Test Error: {e}")
        return jsonify({"error": str(e)}), 400


# ── Admin Contact Settings ──

@settings_bp.route("/admin-contact", methods=["GET"])
def get_admin_contact_public():
    """Get admin contact details (public, no JWT required - used for 403 responses)."""
    try:
        db = get_db()
        settings = db.settings.find_one({})

        if not settings:
            return jsonify({
                "email": "admin@yourdomain.com",
                "phone": ""
            }), 200

        admin_contact = settings.get("admin_contact", {})
        return jsonify({
            "email": admin_contact.get("email", "admin@yourdomain.com"),
            "phone": admin_contact.get("phone", ""),
            "website": admin_contact.get("website", "")
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@settings_bp.route("/admin-contact", methods=["GET"])
@jwt_required_with_role("super_admin")
def get_admin_contact():
    """Get admin contact details (super_admin only)."""
    try:
        db = get_db()
        settings = db.settings.find_one({})

        if not settings:
            return jsonify({
                "email": "admin@yourdomain.com",
                "phone": "",
                "social_media": {
                    "facebook": "",
                    "twitter": "",
                    "instagram": "",
                    "linkedin": ""
                }
            }), 200

        admin_contact = settings.get("admin_contact", {})
        return jsonify({
            "email": admin_contact.get("email", "admin@yourdomain.com"),
            "phone": admin_contact.get("phone", ""),
            "website": admin_contact.get("website", ""),
            "social_media": admin_contact.get("social_media", {
                "facebook": "",
                "twitter": "",
                "instagram": "",
                "linkedin": ""
            })
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@settings_bp.route("/admin-contact", methods=["PUT"])
@jwt_required_with_role("super_admin")
def update_admin_contact():
    """Update admin contact details (super_admin only)."""
    try:
        data = request.get_json() or {}
        db = get_db()

        # Build update document
        admin_contact = {
            "email": data.get("email", "").strip().lower(),
            "phone": data.get("phone", "").strip(),
            "website": data.get("website", "").strip(),
            "social_media": {
                "facebook": data.get("social_media", {}).get("facebook", "").strip(),
                "twitter": data.get("social_media", {}).get("twitter", "").strip(),
                "instagram": data.get("social_media", {}).get("instagram", "").strip(),
                "linkedin": data.get("social_media", {}).get("linkedin", "").strip(),
            }
        }

        # Update or create settings document
        result = db.settings.update_one(
            {},
            {
                "$set": {
                    "admin_contact": admin_contact,
                    "updated_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )

        updated_settings = db.settings.find_one({})

        return jsonify({
            "message": "Admin contact details updated successfully",
            "admin_contact": updated_settings.get("admin_contact", {})
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Security Settings ──

DEFAULT_SECURITY = {
    "jwt_expiry_hours":         8,
    "max_login_attempts":       5,
    "lockout_duration_minutes": 15,
    "show_detailed_errors":     True,
}

@settings_bp.route("/security", methods=["GET"])
@jwt_required_with_role("super_admin")
def get_security_settings():
    try:
        db  = get_db()
        doc = db.settings.find_one({}) or {}
        ss  = {**DEFAULT_SECURITY, **(doc.get("security_settings") or {})}
        return jsonify(ss), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@settings_bp.route("/security", methods=["PUT"])
@jwt_required_with_role("super_admin")
def update_security_settings():
    try:
        data = request.get_json() or {}
        db   = get_db()
        existing = (db.settings.find_one({}) or {}).get("security_settings") or {}

        ss = {
            "jwt_expiry_hours":         int(data.get("jwt_expiry_hours",         existing.get("jwt_expiry_hours",         8))),
            "max_login_attempts":       int(data.get("max_login_attempts",       existing.get("max_login_attempts",       5))),
            "lockout_duration_minutes": int(data.get("lockout_duration_minutes", existing.get("lockout_duration_minutes", 15))),
            "show_detailed_errors":     bool(data.get("show_detailed_errors",    existing.get("show_detailed_errors",     True))),
        }
        # Validate ranges
        ss["jwt_expiry_hours"]         = max(0, min(ss["jwt_expiry_hours"], 720))   # 0=never, max 30 days
        ss["max_login_attempts"]       = max(3, min(ss["max_login_attempts"], 20))
        ss["lockout_duration_minutes"] = max(5, min(ss["lockout_duration_minutes"], 1440))

        db.settings.update_one(
            {}, {"$set": {"security_settings": ss, "updated_at": datetime.now(timezone.utc)}}, upsert=True
        )
        return jsonify({"message": "Security settings saved", "settings": ss}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_security_config(db=None):
    """Load security settings from DB with defaults fallback."""
    try:
        if db is None:
            db = get_db()
        doc = db.settings.find_one({}) or {}
        return {**DEFAULT_SECURITY, **(doc.get("security_settings") or {})}
    except Exception:
        return DEFAULT_SECURITY


# ── Notification Settings ──

DEFAULT_NOTIF_SETTINGS = {
    "in_app_enabled":  True,
    "push_enabled":    True,
    "email_enabled":   True,
    "vapid_public_key":  "",
    "vapid_private_key": "",
    "vapid_email":       "",
}

@settings_bp.route("/notifications", methods=["GET"])
@jwt_required_with_role("super_admin")
def get_notification_settings():
    try:
        db = get_db()
        doc = db.settings.find_one({}) or {}
        ns = {**DEFAULT_NOTIF_SETTINGS, **(doc.get("notification_settings") or {})}
        if ns.get("vapid_private_key"):
            ns["vapid_private_key"] = "••••••••"
        return jsonify(ns), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@settings_bp.route("/notifications", methods=["PUT"])
@jwt_required_with_role("super_admin")
def update_notification_settings():
    try:
        data = request.get_json() or {}
        db   = get_db()
        existing = (db.settings.find_one({}) or {}).get("notification_settings") or {}

        ns = {
            "in_app_enabled":  bool(data.get("in_app_enabled",  existing.get("in_app_enabled",  True))),
            "push_enabled":    bool(data.get("push_enabled",     existing.get("push_enabled",     True))),
            "email_enabled":   bool(data.get("email_enabled",    existing.get("email_enabled",    True))),
            "vapid_public_key": data.get("vapid_public_key",  existing.get("vapid_public_key",  "")).strip(),
            "vapid_email":      data.get("vapid_email",       existing.get("vapid_email",       "")).strip(),
        }
        priv = data.get("vapid_private_key", "")
        ns["vapid_private_key"] = existing.get("vapid_private_key", "") if priv == "••••••••" else priv.strip()

        db.settings.update_one(
            {}, {"$set": {"notification_settings": ns, "updated_at": datetime.now(timezone.utc)}}, upsert=True
        )

        import os
        if ns["vapid_public_key"]:  os.environ["VAPID_PUBLIC_KEY"]  = ns["vapid_public_key"]
        if ns["vapid_private_key"]: os.environ["VAPID_PRIVATE_KEY"] = ns["vapid_private_key"]
        if ns["vapid_email"]:       os.environ["VAPID_EMAIL"]        = f"mailto:{ns['vapid_email'].replace('mailto:','')}"

        return jsonify({"message": "Notification settings saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
