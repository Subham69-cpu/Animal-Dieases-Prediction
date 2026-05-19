"""Aggregated stats for dashboards."""
from bson import ObjectId
from bson.errors import InvalidId

from ..extensions import get_db


def user_dashboard(user_id: str):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    try:
        uid = ObjectId(user_id)
    except InvalidId:
        return {"error": "Invalid user"}, 400
    pred_count = db.predictions.count_documents({"user_id": uid})
    appt_count = db.appointments.count_documents({"user_id": uid})
    animals = list(db.animals.find({"user_id": uid}))
    recent_preds = list(
        db.predictions.find({"user_id": uid}).sort("created_at", -1).limit(5)
    )
    for p in recent_preds:
        p["id"] = str(p.pop("_id"))
        p["user_id"] = str(p.pop("user_id"))
    return {
        "total_predictions": pred_count,
        "total_appointments": appt_count,
        "saved_animals": [{"id": str(a["_id"]), "name": a.get("name"), "species": a.get("species")} for a in animals],
        "recent_predictions": recent_preds,
    }, 200


def doctor_dashboard(user_id: str, email: str):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    doc = db.doctors.find_one({"contact_email": email})
    if not doc:
        return {"upcoming_appointments": [], "message": "No doctor profile linked to this account."}, 200
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    cur = db.appointments.find({"doctor_id": doc["_id"], "scheduled_at": {"$gte": now}, "status": {"$ne": "cancelled"}}).sort(
        "scheduled_at", 1
    )
    items = []
    for a in cur.limit(20):
        u = db.users.find_one({"_id": a["user_id"]})
        items.append(
            {
                "id": str(a["_id"]),
                "scheduled_at": a["scheduled_at"].isoformat() if hasattr(a["scheduled_at"], "isoformat") else str(a["scheduled_at"]),
                "patient_email": u.get("email") if u else "",
                "animal_name": a.get("animal_name", ""),
                "status": a.get("status"),
            }
        )
    total = db.appointments.count_documents({"doctor_id": doc["_id"]})
    return {"upcoming_appointments": items, "total_consultations": total}, 200


def admin_dashboard():
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    users = db.users.count_documents({})
    preds = db.predictions.count_documents({})
    appts = db.appointments.count_documents({})
    # simple disease trend from predictions
    pipeline = [
        {"$group": {"_id": "$final_prediction", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    trends = list(db.predictions.aggregate(pipeline))
    return {
        "total_users": users,
        "total_predictions": preds,
        "total_appointments": appts,
        "disease_trends": [{"disease": t["_id"], "count": t["count"]} for t in trends],
        "model_note": "See /train endpoints and ml_model/ for accuracy metrics after training.",
    }, 200
