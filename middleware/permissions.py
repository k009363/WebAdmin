"""Page permission helpers for admins."""
from services.db import get_db


def can_access_page(admin_id, page_name):
    """
    Check if admin has permission for a specific page.
    Both admin and super_admin need explicit page permissions.
    Returns True if admin can access the page, False otherwise.
    """
    try:
        db = get_db()
        admin = db.admins.find_one({"_id": admin_id})
        if not admin:
            return False

        # Both admin and super_admin need explicit permissions
        permissions = admin.get("page_permissions", [])
        return page_name in permissions

    except Exception:
        return False


def get_admin_visibility_filter(admin_id):
    """
    Get MongoDB filter for admin resource visibility.
    Super admin sees all resources. Regular admin sees only their own.
    Returns: { "admin_id": admin_id } for regular admin, {} for super admin
    """
    try:
        db = get_db()
        admin = db.admins.find_one({"_id": admin_id})
        if not admin:
            return {}

        # Super admin sees everything
        if admin.get("role") == "super_admin":
            return {}

        # Regular admin sees only own resources
        return {"admin_id": admin_id}

    except Exception:
        return {"admin_id": admin_id}
