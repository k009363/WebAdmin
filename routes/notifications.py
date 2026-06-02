"""Notification system — in-app + web push."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.db import get_db, to_json
from services.push_service import send_push_to_admins, VAPID_PUBLIC_KEY
from bson import ObjectId
from datetime import datetime, timezone, timedelta
import os

notifications_bp = Blueprint("notifications", __name__)


# ── Helpers ────────────────────────────────────────────────────

def is_in_app_enabled(db) -> bool:
    try:
        doc = db.settings.find_one({}) or {}
        return (doc.get("notification_settings") or {}).get("in_app_enabled", True)
    except Exception:
        return True


def create_notification(db, admin_id, notif_type: str, title: str, message: str, metadata: dict = None):
    """Insert a notification record for a specific admin (skipped if in-app disabled)."""
    if not is_in_app_enabled(db):
        return
    db.notifications.insert_one({
        "admin_id":   admin_id,
        "type":       notif_type,
        "title":      title,
        "message":    message,
        "metadata":   metadata or {},
        "read":       False,
        "created_at": datetime.now(timezone.utc),
    })


def notify_new_domain(db, domain_doc, creating_admin_id):
    """Called after domain creation — notify super admin."""
    super_admins = list(db.admins.find({"role": "super_admin"}))
    msg = f"New domain '{domain_doc.get('full_key')}' was created."
    for sa in super_admins:
        if sa["_id"] != creating_admin_id:
            create_notification(db, sa["_id"], "new_domain", "New Domain Created", msg,
                                {"domain_id": str(domain_doc.get("_id", "")),
                                 "domain_key": domain_doc.get("full_key", "")})
            send_push_to_admins(db, [sa["_id"]], "New Domain Created", msg)


def notify_new_user(db, user_doc, creating_admin_id):
    """Called after user creation — notify super admin."""
    super_admins = list(db.admins.find({"role": "super_admin"}))
    msg = f"New user '{user_doc.get('name')}' ({user_doc.get('email', '')}) was created."
    for sa in super_admins:
        if sa["_id"] != creating_admin_id:
            create_notification(db, sa["_id"], "new_user", "New User Created", msg,
                                {"user_id": str(user_doc.get("_id", "")),
                                 "user_name": user_doc.get("name", "")})
            send_push_to_admins(db, [sa["_id"]], "New User Created", msg)


def notify_subscription_renewed(db, domain_doc, admin_id, sub_type: str, price):
    """Called after subscription renewal — notify super admin."""
    full_key = domain_doc.get("full_key", "")
    price_str = f" (₹{price})" if price else ""
    msg = f"Subscription for '{full_key}' renewed as {sub_type.capitalize()}{price_str}."
    meta = {"domain_id": str(domain_doc.get("_id", "")), "domain_key": full_key, "sub_type": sub_type}
    super_admins = list(db.admins.find({"role": "super_admin"}))
    for sa in super_admins:
        create_notification(db, sa["_id"], "subscription_renewed", "Subscription Renewed", msg, meta)
        send_push_to_admins(db, [sa["_id"]], "Subscription Renewed", msg)
    # Notify admin too if different from super admin
    if admin_id and not any(sa["_id"] == admin_id for sa in super_admins):
        create_notification(db, admin_id, "subscription_renewed", "Subscription Renewed", msg, meta)


def notify_new_contact(db, domain_key: str, submitter_name: str, submitter_email: str):
    """Called after contact form submission — notify domain admin and super admin."""
    msg = f"New contact from {submitter_name} ({submitter_email}) on '{domain_key}'."
    meta = {"domain_key": domain_key, "name": submitter_name, "email": submitter_email}
    domain_doc = db.domains.find_one({"full_key": domain_key}) if domain_key else None
    notified = set()
    if domain_doc and domain_doc.get("admin_id"):
        aid = domain_doc["admin_id"]
        create_notification(db, aid, "new_contact", "New Contact Submission", msg, meta)
        send_push_to_admins(db, [aid], "New Contact Submission", msg)
        notified.add(aid)
    for sa in db.admins.find({"role": "super_admin"}):
        if sa["_id"] not in notified:
            create_notification(db, sa["_id"], "new_contact", "New Contact Submission", msg, meta)


def notify_new_feedback(db, domain_key: str, submitter_name: str, rating):
    """Called after feedback submission — notify domain admin and super admin."""
    stars = "★" * int(rating or 0) if rating else ""
    msg = f"New feedback {stars} from {submitter_name} on '{domain_key}'."
    meta = {"domain_key": domain_key, "name": submitter_name, "rating": str(rating or "")}
    domain_doc = db.domains.find_one({"full_key": domain_key}) if domain_key else None
    notified = set()
    if domain_doc and domain_doc.get("admin_id"):
        aid = domain_doc["admin_id"]
        create_notification(db, aid, "new_feedback", "New Feedback Received", msg, meta)
        send_push_to_admins(db, [aid], "New Feedback Received", msg)
        notified.add(aid)
    for sa in db.admins.find({"role": "super_admin"}):
        if sa["_id"] not in notified:
            create_notification(db, sa["_id"], "new_feedback", "New Feedback Received", msg, meta)


def notify_domain_toggled(db, domain_doc, admin_id, enabled: bool):
    """Called when a domain is enabled/disabled — notify super admin."""
    full_key = domain_doc.get("full_key", "")
    action = "enabled" if enabled else "disabled"
    msg = f"Domain '{full_key}' was {action}."
    meta = {"domain_id": str(domain_doc.get("_id", "")), "domain_key": full_key, "enabled": enabled}
    for sa in db.admins.find({"role": "super_admin"}):
        if sa["_id"] != admin_id:
            create_notification(db, sa["_id"], "domain_toggled",
                                f"Domain {'Enabled' if enabled else 'Disabled'}", msg, meta)


def check_subscription_expiry(db):
    """
    Check domains whose subscription has expired but haven't been notified yet.
    Creates notifications for both super admin and the domain's admin.
    """
    now = datetime.now(timezone.utc)
    # Domains expired and not yet notified
    expired_domains = list(db.domains.find({
        "subscription.end_date": {"$lt": now},
        "subscription_expiry_notified": {"$ne": True}
    }))

    for domain in expired_domains:
        admin_id = domain.get("admin_id")
        full_key = domain.get("full_key", "")
        msg = f"Subscription for domain '{full_key}' has expired. Please renew to keep the website active."
        meta = {"domain_id": str(domain["_id"]), "domain_key": full_key}

        # Notify the domain's admin
        if admin_id:
            create_notification(db, admin_id, "subscription_expired",
                                "Subscription Expired", msg, meta)
            send_push_to_admins(db, [admin_id], "Subscription Expired", msg)

        # Notify super admin too (if different)
        super_admins = list(db.admins.find({"role": "super_admin"}))
        for sa in super_admins:
            if admin_id is None or sa["_id"] != admin_id:
                create_notification(db, sa["_id"], "subscription_expired",
                                    "Subscription Expired", msg, meta)
                send_push_to_admins(db, [sa["_id"]], "Subscription Expired", msg)

        # Mark domain as notified
        db.domains.update_one(
            {"_id": domain["_id"]},
            {"$set": {"subscription_expiry_notified": True}}
        )

    # Also check domains expiring in next 3 days (warning, only once)
    soon = now + timedelta(days=3)
    expiring_soon = list(db.domains.find({
        "subscription.end_date": {"$gte": now, "$lte": soon},
        "subscription_expiry_warning_sent": {"$ne": True}
    }))

    for domain in expiring_soon:
        admin_id = domain.get("admin_id")
        full_key = domain.get("full_key", "")
        end = domain.get("subscription", {}).get("end_date")
        end_str = end.strftime("%d %b %Y") if end else ""
        msg = f"Subscription for '{full_key}' expires on {end_str}. Renew soon to avoid interruption."
        meta = {"domain_id": str(domain["_id"]), "domain_key": full_key}

        if admin_id:
            create_notification(db, admin_id, "subscription_warning",
                                "Subscription Expiring Soon", msg, meta)
            send_push_to_admins(db, [admin_id], "Subscription Expiring Soon", msg)

        super_admins = list(db.admins.find({"role": "super_admin"}))
        for sa in super_admins:
            if admin_id is None or sa["_id"] != admin_id:
                create_notification(db, sa["_id"], "subscription_warning",
                                    "Subscription Expiring Soon", msg, meta)

        db.domains.update_one(
            {"_id": domain["_id"]},
            {"$set": {"subscription_expiry_warning_sent": True}}
        )


# ── API Routes ─────────────────────────────────────────────────

@notifications_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications():
    """Get notifications for the current admin. Also triggers expiry check."""
    db = get_db()
    admin_id = ObjectId(get_jwt_identity())

    # Run expiry check on every poll
    try:
        check_subscription_expiry(db)
    except Exception as e:
        print(f"Expiry check error: {e}")

    limit = min(int(request.args.get("limit", 10)), 50)
    notifications = list(
        db.notifications.find({"admin_id": admin_id})
        .sort("created_at", -1)
        .limit(limit)
    )
    unread_count = db.notifications.count_documents({"admin_id": admin_id, "read": False})

    return jsonify({
        "notifications": to_json(notifications),
        "unread_count":  unread_count
    }), 200


@notifications_bp.route("/<notif_id>/read", methods=["POST"])
@jwt_required()
def mark_read(notif_id):
    db = get_db()
    admin_id = ObjectId(get_jwt_identity())
    db.notifications.update_one(
        {"_id": ObjectId(notif_id), "admin_id": admin_id},
        {"$set": {"read": True}}
    )
    return jsonify({"message": "Marked as read"}), 200


@notifications_bp.route("/read-all", methods=["POST"])
@jwt_required()
def mark_all_read():
    db = get_db()
    admin_id = ObjectId(get_jwt_identity())
    db.notifications.update_many({"admin_id": admin_id, "read": False}, {"$set": {"read": True}})
    return jsonify({"message": "All marked as read"}), 200


@notifications_bp.route("/<notif_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notif_id):
    db = get_db()
    admin_id = ObjectId(get_jwt_identity())
    db.notifications.delete_one({"_id": ObjectId(notif_id), "admin_id": admin_id})
    return jsonify({"message": "Deleted"}), 200


@notifications_bp.route("/clear-all", methods=["DELETE"])
@jwt_required()
def clear_all():
    db = get_db()
    admin_id = ObjectId(get_jwt_identity())
    db.notifications.delete_many({"admin_id": admin_id})
    return jsonify({"message": "All cleared"}), 200


# ── Web Push subscription management ──────────────────────────

@notifications_bp.route("/push/vapid-key", methods=["GET"])
def get_vapid_key():
    """Return the VAPID public key for the frontend to subscribe."""
    return jsonify({"public_key": VAPID_PUBLIC_KEY}), 200


@notifications_bp.route("/push/subscribe", methods=["POST"])
@jwt_required()
def push_subscribe():
    """Save a push subscription for the current admin."""
    db = get_db()
    admin_id = ObjectId(get_jwt_identity())
    data = request.get_json() or {}
    sub_info = data.get("subscription")
    if not sub_info or not sub_info.get("endpoint"):
        return jsonify({"error": "Invalid subscription"}), 400

    # Upsert by endpoint
    db.push_subscriptions.update_one(
        {"endpoint": sub_info["endpoint"]},
        {"$set": {"admin_id": admin_id, "subscription_info": sub_info,
                  "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return jsonify({"message": "Subscribed"}), 200


@notifications_bp.route("/push/unsubscribe", methods=["POST"])
@jwt_required()
def push_unsubscribe():
    db = get_db()
    data = request.get_json() or {}
    endpoint = data.get("endpoint")
    if endpoint:
        db.push_subscriptions.delete_one({"endpoint": endpoint})
    return jsonify({"message": "Unsubscribed"}), 200


@notifications_bp.route("/push/test", methods=["POST"])
@jwt_required()
def test_push():
    """Send a test push notification to the current admin's browser."""
    db = get_db()
    admin_id = ObjectId(get_jwt_identity())

    subs = list(db.push_subscriptions.find({"admin_id": admin_id}))
    if not subs:
        return jsonify({"error": "No push subscription found. Open the admin panel in your browser first to register for push notifications."}), 400

    from services.push_service import send_push
    from services.push_service import get_vapid_keys
    priv, pub, claims = get_vapid_keys(db)

    if not priv:
        return jsonify({"error": "VAPID keys not configured. Add VAPID keys in Settings → Notification Settings."}), 400

    sent = 0
    for sub in subs:
        info = sub.get("subscription_info")
        if info:
            ok = send_push(
                info,
                title="🔔 Test Push Notification",
                body="Push notifications are working correctly!",
                url="/",
                vapid_private=priv,
                vapid_claims=claims,
            )
            if ok:
                sent += 1

    if sent == 0:
        return jsonify({"error": "Failed to send push — check VAPID keys or browser subscription."}), 400

    return jsonify({"message": f"Test push sent to {sent} device(s)!"}), 200
