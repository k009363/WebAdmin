from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from services.db import get_db, to_json
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from middleware.permissions import get_admin_visibility_filter

domains_bp = Blueprint("domains", __name__)


@domains_bp.route("/", methods=["GET"])
@jwt_required()
def list_domains():
    try:
        db = get_db()
        admin_id = ObjectId(get_jwt_identity())

        # Build visibility filter (super_admin sees all, regular admin sees only own)
        visibility_filter = get_admin_visibility_filter(admin_id)

        domains = list(db.domains.find(visibility_filter).sort("created_at", -1))
        return jsonify(to_json(domains)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@domains_bp.route("/", methods=["POST"])
@jwt_required()
def create_domain():
    try:
        data = request.get_json() or {}
        domain = data.get("domain", "").strip().lower().replace("https://", "").replace("http://", "").strip("/")
        path = data.get("path", "").strip().lower().strip("/")
        full_key = f"{domain}/{path}" if path else domain

        db = get_db()
        if db.domains.find_one({"full_key": full_key}):
            return jsonify({"error": f"'{full_key}' already exists"}), 409

        current_admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()
        now = datetime.now(timezone.utc)

        # Determine which admin owns this domain
        # Super admin can explicitly assign a domain to a specific admin
        assign_to = data.get("admin_id")
        if claims.get("role") == "super_admin" and assign_to:
            try:
                admin_id = ObjectId(assign_to)
            except Exception:
                admin_id = current_admin_id
        elif data.get("user_id"):
            # Auto-derive admin_id from the selected user's admin_id
            user = db.users.find_one({"_id": ObjectId(data["user_id"])})
            if user and user.get("admin_id"):
                admin_id = user["admin_id"]
            else:
                admin_id = current_admin_id
        else:
            admin_id = current_admin_id

        doc = {
            "domain": domain,
            "path": path,
            "full_key": full_key,
            "template_id": ObjectId(data["template_id"]) if data.get("template_id") else None,
            "user_id": ObjectId(data["user_id"]) if data.get("user_id") else None,
            "admin_id": admin_id,
            "enabled": True,
            "subscription": {
                "type": "none",
                "start_date": now,
                "end_date": now + timedelta(days=30),  # 30-day trial
                "price": None,
                "is_active": True
            },
            "created_at": now,
            "updated_at": now,
        }
        result = db.domains.insert_one(doc)
        doc["_id"] = result.inserted_id

        try:
            from routes.notifications import notify_new_domain
            notify_new_domain(db, doc, current_admin_id)
        except Exception:
            pass

        return jsonify(to_json(doc)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@domains_bp.route("/<domain_id>", methods=["PUT"])
@jwt_required()
def update_domain(domain_id):
    try:
        data = request.get_json() or {}
        db = get_db()
        admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()

        # Find existing domain
        existing = db.domains.find_one({"_id": ObjectId(domain_id)})
        if not existing:
            return jsonify({"error": "Domain not found"}), 404

        # Permission check: regular admin can only edit their own domains
        if claims.get("role") != "super_admin" and existing.get("admin_id") != admin_id:
            return jsonify({"error": "You can only edit your own domains"}), 403

        update = {"updated_at": datetime.now(timezone.utc)}
        for field in ("domain", "path", "enabled"):
            if field in data:
                update[field] = data[field]
        if "template_id" in data and data["template_id"]:
            update["template_id"] = ObjectId(data["template_id"])
        if "user_id" in data and data["user_id"]:
            update["user_id"] = ObjectId(data["user_id"])

        # Rebuild full_key if domain/path changed — strip protocol if user typed it
        d = update.get("domain", existing["domain"]).replace("https://", "").replace("http://", "").strip("/")
        p = update.get("path", existing.get("path", "")).strip("/")
        update["domain"]   = d
        update["full_key"] = f"{d}/{p}" if p else d

        db.domains.update_one({"_id": ObjectId(domain_id)}, {"$set": update})
        updated = db.domains.find_one({"_id": ObjectId(domain_id)})
        return jsonify(to_json(updated)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@domains_bp.route("/<domain_id>/toggle", methods=["PATCH"])
@jwt_required()
def toggle_domain(domain_id):
    try:
        db = get_db()
        admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()

        doc = db.domains.find_one({"_id": ObjectId(domain_id)})
        if not doc:
            return jsonify({"error": "Domain not found"}), 404

        # Permission check: regular admin can only toggle their own domains
        if claims.get("role") != "super_admin" and doc.get("admin_id") != admin_id:
            return jsonify({"error": "You can only toggle your own domains"}), 403

        new_state = not doc.get("enabled", True)
        db.domains.update_one({"_id": ObjectId(domain_id)}, {"$set": {"enabled": new_state, "updated_at": datetime.now(timezone.utc)}})

        try:
            from routes.notifications import notify_domain_toggled
            notify_domain_toggled(db, doc, admin_id, new_state)
        except Exception:
            pass

        return jsonify({"enabled": new_state}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@domains_bp.route("/<domain_id>", methods=["DELETE"])
@jwt_required()
def delete_domain(domain_id):
    try:
        db = get_db()
        admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()

        # Find domain
        domain = db.domains.find_one({"_id": ObjectId(domain_id)})
        if not domain:
            return jsonify({"error": "Domain not found"}), 404

        # Permission check: regular admin can only delete their own domains
        if claims.get("role") != "super_admin" and domain.get("admin_id") != admin_id:
            return jsonify({"error": "You can only delete your own domains"}), 403

        db.domains.delete_one({"_id": ObjectId(domain_id)})
        return jsonify({"message": "Domain deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@domains_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    try:
        db = get_db()
        admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()

        # Build visibility filter
        visibility_filter = get_admin_visibility_filter(admin_id)

        return jsonify({
            "total": db.domains.count_documents(visibility_filter),
            "enabled": db.domains.count_documents({**visibility_filter, "enabled": True}),
            "disabled": db.domains.count_documents({**visibility_filter, "enabled": False}),
            "users": db.users.count_documents({}),
            "templates": db.templates.count_documents({}),
            "contacts": db.contacts.count_documents({}),
            "feedback": db.feedback.count_documents({}),
            "blog_posts": db.blog_posts.count_documents({}),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
