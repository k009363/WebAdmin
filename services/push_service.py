"""Web Push notification service using VAPID."""
import json
import os
from pywebpush import webpush, WebPushException

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_PUBLIC_KEY  = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_CLAIMS      = {"sub": f"mailto:{os.getenv('VAPID_EMAIL', 'admin@example.com')}"}


def send_push(subscription_info: dict, title: str, body: str, icon: str = "/favicon.ico", url: str = "/",
              vapid_private=None, vapid_claims=None):
    """Send a web push notification to a single subscription."""
    priv   = vapid_private or VAPID_PRIVATE_KEY
    claims = vapid_claims  or VAPID_CLAIMS
    if not priv:
        return False
    try:
        data = json.dumps({"title": title, "body": body, "icon": icon, "url": url})
        webpush(
            subscription_info=subscription_info,
            data=data,
            vapid_private_key=priv,
            vapid_claims=claims,
        )
        return True
    except WebPushException as e:
        print(f"Push error: {e}")
        return False
    except Exception as e:
        print(f"Push unexpected error: {e}")
        return False


def is_push_enabled(db) -> bool:
    """Check if push notifications are enabled in DB settings."""
    try:
        doc = db.settings.find_one({}) or {}
        ns  = doc.get("notification_settings") or {}
        return ns.get("push_enabled", True)
    except Exception:
        return True


def get_vapid_keys(db):
    """Get VAPID keys from DB (overrides .env if set)."""
    try:
        doc = db.settings.find_one({}) or {}
        ns  = doc.get("notification_settings") or {}
        priv = ns.get("vapid_private_key") or VAPID_PRIVATE_KEY
        pub  = ns.get("vapid_public_key")  or VAPID_PUBLIC_KEY
        mail = ns.get("vapid_email")       or VAPID_CLAIMS.get("sub", "")
        return priv, pub, {"sub": f"mailto:{mail.replace('mailto:','')}"}
    except Exception:
        return VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_CLAIMS


def send_push_to_admins(db, admin_ids: list, title: str, body: str, url: str = "/"):
    """Send push to all subscriptions of given admin ids."""
    if not is_push_enabled(db):
        return
    priv, pub, claims = get_vapid_keys(db)
    if not priv:
        return
    for admin_id in admin_ids:
        subs = list(db.push_subscriptions.find({"admin_id": admin_id}))
        for sub in subs:
            info = sub.get("subscription_info")
            if info:
                ok = send_push(info, title, body, url=url, vapid_private=priv, vapid_claims=claims)
                if not ok:
                    # Remove dead subscription
                    db.push_subscriptions.delete_one({"_id": sub["_id"]})
