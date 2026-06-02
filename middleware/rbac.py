"""Role-based access control decorator for JWT-protected endpoints."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def jwt_required_with_role(*required_roles):
    """
    Decorator that checks JWT and validates admin has required role.
    Usage: @jwt_required_with_role("super_admin")
           @jwt_required_with_role("super_admin", "admin")
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")

            if required_roles and role not in required_roles:
                return jsonify({"error": "Insufficient permissions"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
