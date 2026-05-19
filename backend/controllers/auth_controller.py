"""User signup and login."""
import logging
import os

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import get_db
from ..models.db_indexes import utcnow
from ..utils.jwt_auth import create_token

log = logging.getLogger(__name__)


def signup(data: dict) -> tuple[dict, int]:
    db = get_db()
    if db is None:
        return {
            "error": "No database available. Start MongoDB, or set USE_SQLITE_FALLBACK=true (default) to use local SQLite.",
        }, 503
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = data.get("name") or ""
    role = (data.get("role") or "user").lower()
    if role not in ("user", "veterinarian"):
        role = "user"
    if not email or not password:
        return {"error": "Email and password required"}, 400
    if db.users.find_one({"email": email}):
        return {"error": "Email already registered"}, 409
    doc = {
        "email": email,
        "password_hash": generate_password_hash(password),
        "name": name,
        "role": "veterinarian" if role == "veterinarian" else "user",
        "phone": data.get("phone", ""),
        "created_at": utcnow(),
    }
    res = db.users.insert_one(doc)
    log.info("New user registered: %s", email)
    return {"user_id": str(res.inserted_id), "email": email, "role": doc["role"], "name": name}, 201


def login(data: dict, app) -> tuple[dict, int]:
    db = get_db()
    if db is None:
        return {
            "error": "No database available. Start MongoDB, or set USE_SQLITE_FALLBACK=true (default) to use local SQLite.",
        }, 503
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return {"error": "Email and password required"}, 400
    user = db.users.find_one({"email": email})
    if not user or not check_password_hash(user["password_hash"], password):
        return {"error": "Invalid credentials"}, 401
    token = create_token(str(user["_id"]), user["email"], user.get("role", "user"))
    return {
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", ""),
            "role": user.get("role", "user"),
        },
    }, 200


def admin_bootstrap(app):
    """Create default admin user if ADMIN_EMAIL and ADMIN_PASSWORD set."""
    db = get_db()
    if db is None:
        return
    import os

    email = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
    pw = os.environ.get("ADMIN_PASSWORD", "")
    if not email or not pw:
        return
    if db.users.find_one({"email": email}):
        return
    db.users.insert_one(
        {
            "email": email,
            "password_hash": generate_password_hash(pw),
            "name": "Administrator",
            "role": "admin",
            "phone": "",
            "created_at": utcnow(),
        }
    )
    log.info("Admin user created for %s", email)
