from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.db import get_db, to_json
from bson import ObjectId
from datetime import datetime, timezone

users_bp = Blueprint("users", __name__)


@users_bp.route("/", methods=["GET"])
@jwt_required()
def list_users():
    try:
        db = get_db()
        admin_id = ObjectId(get_jwt_identity())
        claims = get_jwt()

        # Super admin sees all users
        if claims.get("role") == "super_admin":
            users = list(db.users.find().sort("created_at", -1))
            return jsonify(to_json(users)), 200

        # Regular admin sees only users they created (by admin_id)
        users = list(db.users.find({"admin_id": admin_id}).sort("created_at", -1))
        return jsonify(to_json(users)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/", methods=["POST"])
@jwt_required()
def create_user():
    data = request.get_json() or {}
    db = get_db()
    admin_id = ObjectId(get_jwt_identity())
    claims = get_jwt()

    # If super_admin is creating a user and specifies assign_to_admin_id, use that
    assign_to = data.get("admin_id")
    if claims.get("role") == "super_admin" and assign_to:
        try:
            owner_admin_id = ObjectId(assign_to)
        except Exception:
            owner_admin_id = admin_id
    else:
        owner_admin_id = admin_id

    doc = {
        "name": data.get("name", "").strip(),
        "email": data.get("email", "").strip().lower(),
        "phone": data.get("phone", "").strip(),
        "company": data.get("company", "").strip(),
        "domain": data.get("domain", "").strip().lower(),
        "admin_id": owner_admin_id,
        "created_at": datetime.now(timezone.utc),
    }
    result = db.users.insert_one(doc)
    doc["_id"] = result.inserted_id

    try:
        from routes.notifications import notify_new_user
        notify_new_user(db, doc, admin_id)
    except Exception:
        pass

    return jsonify(to_json(doc)), 201


@users_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    data = request.get_json() or {}
    db = get_db()
    update = {}
    for field in ("name", "email", "phone", "company", "domain"):
        if field in data:
            update[field] = data[field]
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update})
    updated = db.users.find_one({"_id": ObjectId(user_id)})
    return jsonify(to_json(updated)), 200


@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    db = get_db()
    db.users.delete_one({"_id": ObjectId(user_id)})
    return jsonify({"message": "Deleted"}), 200
