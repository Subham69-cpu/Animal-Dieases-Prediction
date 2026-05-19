"""Pet / livestock profiles for users."""
from bson import ObjectId
from bson.errors import InvalidId

from ..extensions import get_db
from ..models.db_indexes import utcnow


def list_animals(user_id: str):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    try:
        uid = ObjectId(user_id)
    except InvalidId:
        return {"error": "Invalid user"}, 400
    out = []
    for a in db.animals.find({"user_id": uid}):
        out.append(
            {
                "id": str(a["_id"]),
                "name": a.get("name"),
                "species": a.get("species"),
                "notes": a.get("notes", ""),
            }
        )
    return {"animals": out}, 200


def create_animal(user_id: str, body: dict):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    name = (body.get("name") or "").strip()
    species = (body.get("species") or "").strip().lower()
    if not name:
        return {"error": "name required"}, 400
    try:
        uid = ObjectId(user_id)
    except InvalidId:
        return {"error": "Invalid user"}, 400
    doc = {
        "user_id": uid,
        "name": name,
        "species": species,
        "notes": body.get("notes", ""),
        "created_at": utcnow(),
    }
    res = db.animals.insert_one(doc)
    return {"id": str(res.inserted_id)}, 201
