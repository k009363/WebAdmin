from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from bson import ObjectId
import os
import time

_client        = None
_db            = None
_last_fail_at  = 0          # timestamp of last failed attempt
_RETRY_AFTER   = 30         # seconds before trying again after a failure
DB_NAME        = os.getenv("MONGO_DB", "dynamic_websites")


def _build_client(uri: str) -> MongoClient:
    is_atlas = "mongodb+srv" in uri or "mongodb.net" in uri
    if is_atlas:
        return MongoClient(
            uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            retryWrites=True,
            retryReads=True,
            serverSelectionTimeoutMS=8000,   # fail fast — 8s not 15s
            connectTimeoutMS=8000,
            socketTimeoutMS=20000,
            maxPoolSize=10,
            minPoolSize=1,
        )
    return MongoClient(uri, serverSelectionTimeoutMS=5000, maxPoolSize=10)


def get_db(retries: int = 1, delay: float = 0):
    """
    Return the DB connection.
    - If already connected → ping check, return immediately.
    - If last attempt failed < 30s ago → fail fast (no retry wait).
    - On startup (retries=3 passed by seed_admin) → retry with delay.
    """
    global _client, _db, _last_fail_at

    # Already connected — quick liveness check
    if _db is not None:
        try:
            _client.admin.command("ping")
            return _db
        except Exception:
            _client = None
            _db     = None

    # Recently failed — don't hammer Atlas, fail immediately
    now = time.time()
    if _last_fail_at and (now - _last_fail_at) < _RETRY_AFTER and retries == 1:
        raise ConnectionFailure(
            "MongoDB is currently unreachable. "
            f"Next retry in {int(_RETRY_AFTER - (now - _last_fail_at))}s.\n"
            "Possible causes:\n"
            "  1. Atlas cluster is paused → cloud.mongodb.com → Resume\n"
            "  2. IP not whitelisted → Atlas → Network Access → Add IP (or 0.0.0.0/0)\n"
            "  3. Wrong credentials in MONGO_URI"
        )

    uri        = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            _client = _build_client(uri)
            _db     = _client[DB_NAME]
            _client.admin.command("ping")
            _last_fail_at = 0   # reset on success
            if attempt > 1:
                print(f"[db] Connected on attempt {attempt}")
            return _db
        except Exception as e:
            last_error    = e
            _last_fail_at = time.time()
            _client = None
            _db     = None
            if attempt < retries:
                print(f"[db] Connection attempt {attempt} failed: {e.__class__.__name__} — retrying in {delay}s…")
                time.sleep(delay)

    raise ConnectionFailure(
        f"Could not connect to MongoDB.\n"
        f"Last error: {last_error}\n\n"
        "Possible causes:\n"
        "  1. Atlas cluster is paused → cloud.mongodb.com → Resume\n"
        "  2. IP not whitelisted → Atlas → Network Access → Add IP (or 0.0.0.0/0)\n"
        "  3. Wrong credentials in MONGO_URI\n"
        "  4. No internet connection"
    )


def to_json(doc):
    """Recursively convert ObjectId → str for JSON serialisation."""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [to_json(d) for d in doc]
    if isinstance(doc, dict):
        return {k: (str(v) if isinstance(v, ObjectId) else to_json(v)) for k, v in doc.items()}
    return doc
