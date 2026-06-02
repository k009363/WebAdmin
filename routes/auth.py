from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from services.db import get_db, to_json
from bson import ObjectId
from middleware.rbac import jwt_required_with_role
from middleware.permissions import get_admin_visibility_filter
import bcrypt, os

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    db = get_db()

    # Load security config
    from routes.settings import get_security_config
    sec = get_security_config(db)
    max_attempts       = sec.get("max_login_attempts", 5)
    lockout_minutes    = sec.get("lockout_duration_minutes", 15)
    jwt_expiry_hours   = sec.get("jwt_expiry_hours", 8)

    admin = db.admins.find_one({"username": username})
    if not admin:
        return jsonify({"error": "Invalid credentials"}), 401

    # ── Check lockout ──────────────────────────────────────────
    now = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
    failed        = admin.get("failed_login_attempts", 0)
    locked_until  = admin.get("login_locked_until")

    if locked_until:
        if isinstance(locked_until, str):
            from dateutil import parser
            locked_until = parser.parse(locked_until)
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=__import__('datetime').timezone.utc)
        if now < locked_until:
            remaining = int((locked_until - now).total_seconds() / 60) + 1
            return jsonify({
                "error": f"Account locked due to too many failed attempts. Try again in {remaining} minute(s)."
            }), 429

    # ── Verify password ────────────────────────────────────────
    if not bcrypt.checkpw(password.encode(), admin["password_hash"]):
        new_failed = failed + 1
        update = {"failed_login_attempts": new_failed}
        if new_failed >= max_attempts:
            from datetime import timedelta
            update["login_locked_until"] = now + timedelta(minutes=lockout_minutes)
            db.admins.update_one({"_id": admin["_id"]}, {"$set": update})
            return jsonify({
                "error": f"Too many failed attempts. Account locked for {lockout_minutes} minutes."
            }), 429
        db.admins.update_one({"_id": admin["_id"]}, {"$set": update})
        remaining_attempts = max_attempts - new_failed
        return jsonify({
            "error": f"Invalid credentials. {remaining_attempts} attempt(s) remaining before lockout."
        }), 401

    # ── Success — reset failed attempts ───────────────────────
    db.admins.update_one(
        {"_id": admin["_id"]},
        {"$set": {"failed_login_attempts": 0, "login_locked_until": None, "last_login": now}}
    )

    # ── Build JWT with expiry from DB settings ─────────────────
    from datetime import timedelta
    expires = timedelta(hours=jwt_expiry_hours) if jwt_expiry_hours > 0 else False

    additional_claims = {
        "role":             admin.get("role", "admin"),
        "page_permissions": admin.get("page_permissions", []),
        "email":            admin.get("email", ""),
    }

    token = create_access_token(
        identity=str(admin["_id"]),
        additional_claims=additional_claims,
        expires_delta=expires
    )

    return jsonify({
        "token":    token,
        "username": username,
        "role":     admin.get("role", "admin"),
        "email":    admin.get("email", ""),
        "expires_in_hours": jwt_expiry_hours if jwt_expiry_hours > 0 else None,
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_admin():
    """Get current logged-in admin details with role and permissions."""
    try:
        admin_id = get_jwt_identity()
        claims = get_jwt()
        db = get_db()

        admin = db.admins.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        return jsonify({
            "id": str(admin["_id"]),
            "username": admin.get("username"),
            "email": admin.get("email", ""),
            "phone": admin.get("phone", ""),
            "role": admin.get("role", "admin"),
            "page_permissions": admin.get("page_permissions", []),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    try:
        data = request.get_json() or {}
        old_pw = data.get("old_password", "")
        new_pw = data.get("new_password", "")

        if not old_pw or not new_pw:
            return jsonify({"error": "Missing password fields"}), 400

        admin_id = get_jwt_identity()
        db = get_db()

        admin = db.admins.find_one({"_id": ObjectId(admin_id)})
        if not admin or not bcrypt.checkpw(old_pw.encode(), admin["password_hash"]):
            return jsonify({"error": "Invalid credentials"}), 401

        hashed = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
        db.admins.update_one(
            {"_id": admin["_id"]},
            {"$set": {"password_hash": hashed, "updated_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc)}}
        )
        return jsonify({"message": "Password updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Admin Management (Super Admin Only) ──

@auth_bp.route("/admin-list", methods=["GET"])
@jwt_required_with_role("super_admin")
def list_admins():
    """List all admins (super_admin only)."""
    try:
        db = get_db()
        admins = list(db.admins.find({}))

        return jsonify([{
            "id": str(admin["_id"]),
            "username": admin.get("username"),
            "email": admin.get("email", ""),
            "phone": admin.get("phone", ""),
            "role": admin.get("role", "admin"),
            "page_permissions": admin.get("page_permissions", []),
            "created_at": admin.get("created_at", "").isoformat() if admin.get("created_at") else "",
        } for admin in admins]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/admin-create", methods=["POST"])
@jwt_required_with_role("super_admin")
def create_admin():
    """Create new admin (super_admin only)."""
    try:
        data = request.get_json() or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        email = data.get("email", "").strip().lower()
        phone = data.get("phone", "").strip()
        role = data.get("role", "admin")
        page_permissions = data.get("page_permissions", [])

        # Validate required fields
        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400

        # Cannot create another super_admin
        if role == "super_admin":
            return jsonify({"error": "Cannot create super_admin"}), 403

        db = get_db()

        # Check if username exists
        if db.admins.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 400

        # Get current admin ID
        current_id = ObjectId(get_jwt_identity())

        # Create new admin
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        now = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)

        result = db.admins.insert_one({
            "username": username,
            "password_hash": hashed,
            "email": email,
            "phone": phone,
            "role": role,
            "created_by_id": current_id,
            "page_permissions": page_permissions,
            "created_at": now,
            "updated_at": now,
        })

        new_admin = db.admins.find_one({"_id": result.inserted_id})

        return jsonify({
            "id": str(new_admin["_id"]),
            "username": new_admin.get("username"),
            "email": new_admin.get("email", ""),
            "phone": new_admin.get("phone", ""),
            "role": new_admin.get("role", "admin"),
            "page_permissions": new_admin.get("page_permissions", []),
            "message": f"Admin '{username}' created successfully"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/admin/<admin_id>", methods=["PUT"])
@jwt_required_with_role("super_admin")
def update_admin(admin_id):
    """Update admin role/permissions (super_admin only)."""
    try:
        data = request.get_json() or {}
        role = data.get("role")
        page_permissions = data.get("page_permissions")
        email = data.get("email")
        phone = data.get("phone")

        db = get_db()

        # Find admin
        admin = db.admins.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        # Cannot change role to super_admin
        if role == "super_admin":
            return jsonify({"error": "Cannot set role to super_admin"}), 403

        # Update allowed fields
        update_data = {"updated_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc)}

        if role is not None:
            update_data["role"] = role
        if page_permissions is not None:
            update_data["page_permissions"] = page_permissions
        if email is not None:
            update_data["email"] = email.strip().lower()
        if phone is not None:
            update_data["phone"] = phone.strip()

        db.admins.update_one({"_id": ObjectId(admin_id)}, {"$set": update_data})

        updated = db.admins.find_one({"_id": ObjectId(admin_id)})

        return jsonify({
            "id": str(updated["_id"]),
            "username": updated.get("username"),
            "email": updated.get("email", ""),
            "phone": updated.get("phone", ""),
            "role": updated.get("role", "admin"),
            "page_permissions": updated.get("page_permissions", []),
            "message": "Admin updated successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/admin/<admin_id>/reset-password", methods=["POST"])
@jwt_required_with_role("super_admin")
def reset_admin_password(admin_id):
    """Reset admin password (super_admin only)."""
    try:
        data = request.get_json() or {}
        new_password = data.get("new_password", "").strip()

        if not new_password or len(new_password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        db = get_db()
        admin = db.admins.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        if admin.get("role") == "super_admin":
            return jsonify({"error": "Cannot reset super_admin password"}), 403

        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        db.admins.update_one(
            {"_id": ObjectId(admin_id)},
            {"$set": {"password_hash": hashed, "updated_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc)}}
        )
        return jsonify({"message": f"Password reset for '{admin.get('username')}' successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/admin/<admin_id>", methods=["DELETE"])
@jwt_required_with_role("super_admin")
def delete_admin(admin_id):
    """Delete admin (super_admin only, cannot delete self)."""
    try:
        current_id = ObjectId(get_jwt_identity())

        # Cannot delete self
        if str(current_id) == admin_id:
            return jsonify({"error": "Cannot delete yourself"}), 403

        db = get_db()

        # Find and delete admin
        admin = db.admins.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        # Cannot delete super_admin
        if admin.get("role") == "super_admin":
            return jsonify({"error": "Cannot delete super_admin"}), 403

        db.admins.delete_one({"_id": ObjectId(admin_id)})

        return jsonify({"message": f"Admin '{admin.get('username')}' deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
