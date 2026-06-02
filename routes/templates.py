from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.db import get_db, to_json
from services.cloudinary_service import upload_from_settings
from bson import ObjectId
from datetime import datetime, timezone

templates_bp = Blueprint("templates", __name__)

# Default blank config structure
BLANK_CONFIG = {
    "siteId": "",
    "logo": "",
    "theme": {
        "primaryColor": "#4f46e5", "secondaryColor": "#06b6d4",
        "accentColor": "#f59e0b", "bgColor": "#ffffff",
        "textColor": "#1f2937", "mutedColor": "#6b7280",
        "darkBg": "#0f172a", "fontBody": "'Inter', sans-serif",
        "fontHeading": "'Poppins', sans-serif"
    },
    "header": {"template": 1, "phone": "", "email": "",
        "navLinks": [
            {"label": "Home", "page": "home"},
            {"label": "Services", "page": "services"},
            {"label": "Achievements", "page": "achievements"},
            {"label": "About Us", "page": "about"},
            {"label": "Blog", "page": "blog"},
            {"label": "Pricing", "page": "pricing"},
            {"label": "Contact", "page": "contact"},
            {"label": "Feedback", "page": "feedback"}
        ]
    },
    "footer": {"template": 1, "description": "", "address": "", "phone": "", "email": "", "copyrightYear": 2024},
    "socialLinks": {"facebook": "", "twitter": "", "instagram": "", "linkedin": ""},
    "pages": {
        "home": {"template": 1, "titleTemplate": 1, "title": "", "subtitle": "", "heroImage": "", "features": [], "stats": [], "testimonials": []},
        "services": {"template": 1, "titleTemplate": 1, "title": "Our Services", "subtitle": "", "heroImage": "", "items": []},
        "achievements": {"template": 1, "titleTemplate": 1, "title": "Achievements", "subtitle": "", "heroImage": "", "awards": [], "milestones": [], "stats": []},
        "about": {"template": 1, "titleTemplate": 1, "title": "About Us", "subtitle": "", "heroImage": "", "story": "", "mission": "", "vision": "", "values": [], "team": []},
        "blog": {"template": 1, "titleTemplate": 1, "title": "Blog", "subtitle": "", "heroImage": "", "enabled": True, "description": ""},
        "pricing": {"template": 1, "titleTemplate": 1, "title": "Pricing", "subtitle": "", "heroImage": "", "enabled": True, "plans": []},
        "contact": {"template": 1, "titleTemplate": 1, "title": "Contact Us", "subtitle": "", "heroImage": "", "address": "", "phone": "", "email": "", "officeHours": "", "offices": []},
        "feedback": {"template": 1, "titleTemplate": 1, "title": "Feedback", "subtitle": "", "heroImage": "", "categories": ["General", "Quality", "Support", "Other"]}
    }
}


@templates_bp.route("/", methods=["GET"])
@jwt_required()
def list_templates():
    db = get_db()
    templates = list(db.templates.find({}, {"config": 0}).sort("created_at", -1))
    return jsonify(to_json(templates)), 200


@templates_bp.route("/<tmpl_id>", methods=["GET"])
@jwt_required()
def get_template(tmpl_id):
    db = get_db()
    tmpl = db.templates.find_one({"_id": ObjectId(tmpl_id)})
    return jsonify(to_json(tmpl)), 200


@templates_bp.route("/", methods=["POST"])
@jwt_required()
def create_template():
    data = request.get_json() or {}
    db = get_db()
    import copy
    config = data.get("config") or copy.deepcopy(BLANK_CONFIG)
    config["siteId"] = data.get("name", "").lower().replace(" ", "_")
    doc = {
        "name": data.get("name", "Untitled Template"),
        "description": data.get("description", ""),
        "thumbnail_url": data.get("thumbnail_url", ""),
        "config": config,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    result = db.templates.insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(to_json({**doc, "config": None})), 201


@templates_bp.route("/<tmpl_id>", methods=["PUT"])
@jwt_required()
def update_template(tmpl_id):
    data = request.get_json() or {}
    db = get_db()
    update = {"updated_at": datetime.now(timezone.utc)}
    for field in ("name", "description", "thumbnail_url", "config"):
        if field in data:
            update[field] = data[field]
    db.templates.update_one({"_id": ObjectId(tmpl_id)}, {"$set": update})
    updated = db.templates.find_one({"_id": ObjectId(tmpl_id)}, {"config": 0})
    return jsonify(to_json(updated)), 200


@templates_bp.route("/<tmpl_id>/toggle", methods=["PATCH"])
@jwt_required()
def toggle_template(tmpl_id):
    db = get_db()
    doc = db.templates.find_one({"_id": ObjectId(tmpl_id)})
    if not doc:
        return jsonify({"error": "Not found"}), 404
    new_state = not doc.get("enabled", True)
    db.templates.update_one({"_id": ObjectId(tmpl_id)}, {"$set": {"enabled": new_state, "updated_at": datetime.now(timezone.utc)}})
    return jsonify({"enabled": new_state}), 200


@templates_bp.route("/<tmpl_id>", methods=["DELETE"])
@jwt_required()
def delete_template(tmpl_id):
    db = get_db()
    db.templates.delete_one({"_id": ObjectId(tmpl_id)})
    return jsonify({"message": "Deleted"}), 200


@templates_bp.route("/upload-image", methods=["POST"])
@jwt_required()
def upload_image():
    db = get_db()
    settings_doc = db.settings.find_one({})
    settings = to_json(settings_doc) if settings_doc else {}

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    folder = request.form.get("folder", "templates")
    try:
        url = upload_from_settings(file.stream, folder=folder, settings=settings)
        return jsonify({"url": url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
