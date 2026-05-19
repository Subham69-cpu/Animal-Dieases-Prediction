"""MongoDB document helpers and indexes."""
from datetime import datetime, timezone

from pymongo import ASCENDING


def utcnow():
    return datetime.now(timezone.utc)


def ensure_indexes(db):
    if db is None:
        return
    db.users.create_index("email", unique=True)
    db.appointments.create_index([("user_id", ASCENDING), ("scheduled_at", ASCENDING)])
    db.predictions.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
    db.animals.create_index([("user_id", ASCENDING), ("name", ASCENDING)])
