"""
Dynamic Websites — Admin API
Port: 5001
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os, bcrypt

load_dotenv()

FLASK_ENV = os.getenv("FLASK_ENV", "development")
IS_PROD   = FLASK_ENV == "production"

app = Flask(__name__)

# ── CORS ──────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
if IS_PROD and ALLOWED_ORIGINS != "*":
    origins = [o.strip() for o in ALLOWED_ORIGINS.split(",")]
else:
    origins = "*"
CORS(app, resources={r"/api/*": {"origins": origins}})

# ── JWT ───────────────────────────────────────────────────────
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False   # controlled per-login from DB

jwt = JWTManager(app)

# ── Rate Limiter ──────────────────────────────────────────────
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per minute"],
    storage_uri="memory://",
)

# ── Security Headers ──────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"]        = "SAMEORIGIN"
    response.headers["X-XSS-Protection"]       = "1; mode=block"
    response.headers["Referrer-Policy"]         = "strict-origin"
    if IS_PROD:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# ── Global error handlers (respects show_detailed_errors) ─────
def _error_detail(e):
    try:
        from services.db import get_db
        from routes.settings import get_security_config
        cfg = get_security_config(get_db())
        if cfg.get("show_detailed_errors", True):
            return str(e)
    except Exception:
        pass
    return "An unexpected error occurred. Please try again."

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({"error": "Too many requests. Please slow down and try again."}), 429

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": _error_detail(e)}), 500

# ── Register blueprints ────────────────────────────────────────
from routes.auth import auth_bp
from routes.domains import domains_bp
from routes.users import users_bp
from routes.templates import templates_bp
from routes.settings import settings_bp
from routes.contact import contact_bp
from routes.feedback import feedback_bp
from routes.blog import blog_bp
from routes.subscriptions import subscriptions_bp
from routes.notifications import notifications_bp
from routes.site_config import site_config_bp   # public — no JWT

app.register_blueprint(auth_bp,          url_prefix="/api/auth")
app.register_blueprint(domains_bp,       url_prefix="/api/domains")
app.register_blueprint(users_bp,         url_prefix="/api/users")
app.register_blueprint(templates_bp,     url_prefix="/api/templates")
app.register_blueprint(settings_bp,      url_prefix="/api/settings")
app.register_blueprint(contact_bp,       url_prefix="/api/contacts")
app.register_blueprint(feedback_bp,      url_prefix="/api/feedback")
app.register_blueprint(blog_bp,          url_prefix="/api/blog")
app.register_blueprint(subscriptions_bp, url_prefix="/api/subscriptions")
app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
app.register_blueprint(site_config_bp,   url_prefix="/api")

# Apply rate limits — only login endpoint gets strict limit, not the whole auth blueprint
limiter.limit("30 per minute")(contact_bp)
limiter.limit("30 per minute")(feedback_bp)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "admin-api", "env": FLASK_ENV}), 200


# ── Bootstrap default admin account ───────────────────────────
def seed_admin():
    from services.db import get_db
    from pymongo.errors import ConnectionFailure
    try:
        db = get_db(retries=3, delay=2.0)
        if db.admins.count_documents({}) == 0:
            username = os.getenv("ADMIN_USERNAME", "admin")
            password = os.getenv("ADMIN_PASSWORD", "admin123")
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            db.admins.insert_one({"username": username, "password_hash": hashed})
            print(f"[seed] Admin created: {username} / {password}")
        else:
            print("[db] Connected to MongoDB successfully.")
    except ConnectionFailure as e:
        print(f"\n{'='*60}")
        print("WARNING: Could not connect to MongoDB at startup.")
        print(str(e))
        print(f"{'='*60}")
        print("App will start anyway — fix the DB connection and retry.\n")


if __name__ == "__main__":
    seed_admin()
    port = int(os.getenv("PORT", 5000))
    debug = not IS_PROD
    print(f"[app] Starting in {'PRODUCTION' if IS_PROD else 'DEVELOPMENT'} mode (debug={debug})")
    app.run(debug=debug, host="0.0.0.0", port=port)
