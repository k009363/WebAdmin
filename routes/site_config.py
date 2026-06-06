"""
Public endpoint — no JWT required.
Called by the website frontend to get its configuration.
Looks up domain + path in MongoDB and returns the matching template config.
"""
from flask import Blueprint, request, jsonify
from services.db import get_db, to_json
from datetime import datetime, timezone

site_config_bp = Blueprint("site_config", __name__)

# Dev/local IPs: skip the domain↔path template-match check
DEV_HOSTS = {"localhost", "127.0.0.1", "10.139.182.125"}


def _forbidden(detail, db=None):
    """Build 403 response with admin contact details from DB settings."""
    admin_contact = {"email": "", "phone": ""}
    if db is not None:
        try:
            settings = db.settings.find_one({}) or {}
            contact = settings.get("admin_contact") or {}
            admin_contact = {
                "email": contact.get("email", ""),
                "phone": contact.get("phone", "")
            }
        except Exception:
            pass

    return {
        "error": "Access denied",
        "detail": detail,
        "adminContact": admin_contact,
    }


@site_config_bp.route("/site-config", methods=["GET"])
def site_config():
    try:
        # ?domain= param lets the website frontend pass its own domain
        # (needed when the backend is on a different host, e.g. Render vs Netlify)
        domain_param = (request.args.get("domain") or "").lower().strip("/").replace("http://", "").replace("https://", "").split(":")[0]

        if domain_param:
            domain = domain_param
            host = domain_param
        else:
            host = (request.headers.get("X-Forwarded-Host") or request.host or "").lower()
            host = host.replace("http://", "").replace("https://", "").strip("/")
            domain = host.split(":")[0]

        import re
        raw_path = (request.args.get("path") or "").lower()
        path_slug = re.sub(r'/+', '/', raw_path).strip("/") or None

        db = get_db()

        # ── Build candidate full_keys ──────────────────────────────
        if path_slug:
            keys = [f"{host}/{path_slug}", f"{domain}/{path_slug}"]
        else:
            keys = [host, domain]

        # ── Find domain record in MongoDB ─────────────────────────
        domain_doc = None
        for key in keys:
            try:
                domain_doc = db.domains.find_one({"full_key": key})
                if domain_doc:
                    break
            except Exception as e:
                print(f"Error finding domain with key {key}: {e}")
                continue

        # Dev hosts: if combo not found, try path-only match
        if not domain_doc and domain in DEV_HOSTS and path_slug:
            try:
                domain_doc = db.domains.find_one({
                    "full_key": {"$in": [path_slug, f"localhost/{path_slug}"]}
                })
            except Exception as e:
                print(f"Error finding domain by path slug: {e}")

        if not domain_doc:
            return jsonify(_forbidden(
                f"Domain '{domain}{'/' + path_slug if path_slug else ''}' is not registered.",
                db
            )), 403

        # ── Check subscription expiry ────────────────────────────────
        subscription = domain_doc.get("subscription") or {}
        end_date = subscription.get("end_date")
        if end_date:
            try:
                # Compare with current time
                if isinstance(end_date, str):
                    from dateutil import parser
                    end_date = parser.parse(end_date)

                now = datetime.now(timezone.utc)
                if end_date < now:
                    return jsonify(_forbidden(
                        "Subscription has expired. Please renew to continue accessing this site.",
                        db
                    )), 403
            except Exception as e:
                print(f"Error checking subscription: {e}")

        # ── Check enabled flag ────────────────────────────────────
        if not domain_doc.get("enabled", True):
            return jsonify(_forbidden(
                "This site is currently disabled.",
                db
            )), 403

        # ── Load template config ───────────────────────────────────
        if not domain_doc.get("template_id"):
            return jsonify({"error": "No template assigned to this domain."}), 400

        try:
            template_doc = db.templates.find_one({"_id": domain_doc["template_id"]})
        except Exception as e:
            print(f"Error finding template: {e}")
            return jsonify({"error": "Failed to load template configuration."}), 500

        if not template_doc:
            return jsonify({"error": "Template not found."}), 404

        if not template_doc.get("config"):
            return jsonify({"error": "Template configuration is empty."}), 500

        return jsonify(to_json(template_doc["config"])), 200

    except Exception as e:
        print(f"Unexpected error in site_config: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server error", "detail": str(e)}), 500
