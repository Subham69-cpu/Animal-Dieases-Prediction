"""JWT creation, validation, and role-based decorators."""
import functools
from datetime import datetime, timezone

import jwt
from flask import current_app, jsonify, request


def _utc_now():
    return datetime.now(timezone.utc)


def create_token(user_id: str, email: str, role: str) -> str:
    secret = current_app.config["JWT_SECRET"]
    exp = _utc_now() + current_app.config["JWT_EXPIRATION"]
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": exp,
        "iat": _utc_now(),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def token_required(roles=None):
    """Flask route decorator: require Bearer JWT; optional list of allowed roles."""

    if roles is not None and not isinstance(roles, (list, tuple)):
        roles = [roles]

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid Authorization header"}), 401
            token = auth[7:].strip()
            data = decode_token(token)
            if not data:
                return jsonify({"error": "Invalid or expired token"}), 401
            if roles and data.get("role") not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            request.user_id = data["sub"]
            request.user_email = data.get("email")
            request.user_role = data.get("role")
            return f(*args, **kwargs)

        return wrapped

    return decorator
