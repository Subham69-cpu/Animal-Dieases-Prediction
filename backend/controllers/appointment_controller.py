"""Appointment booking and updates."""
import logging
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId

from ..extensions import get_db
from ..models.db_indexes import utcnow
from ..utils.email_util import send_email

log = logging.getLogger(__name__)


def _parse_dt(s: str):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def book_appointment(user_id: str, body: dict):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    doctor_id = body.get("doctor_id")
    scheduled = body.get("scheduled_at")
    notes = body.get("notes", "")
    animal_name = body.get("animal_name", "")
    if not doctor_id or not scheduled:
        return {"error": "doctor_id and scheduled_at (ISO8601) required"}, 400
    try:
        doc_oid = ObjectId(doctor_id)
        usr_oid = ObjectId(user_id)
    except InvalidId:
        return {"error": "Invalid id format"}, 400
    if not db.doctors.find_one({"_id": doc_oid}):
        return {"error": "Doctor not found"}, 404
    dt = _parse_dt(scheduled)
    if dt is None:
        return {"error": "Invalid scheduled_at"}, 400
    appt = {
        "user_id": usr_oid,
        "doctor_id": doc_oid,
        "scheduled_at": dt,
        "status": "confirmed",
        "notes": notes,
        "animal_name": animal_name,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    res = db.appointments.insert_one(appt)
    user = db.users.find_one({"_id": usr_oid})
    doctor = db.doctors.find_one({"_id": doc_oid})
    if user and doctor:
        send_email(
            user.get("email", ""),
            "Appointment confirmed",
            f"Your appointment with {doctor.get('name')} is confirmed for {scheduled}.\n"
            f"Clinic: {doctor.get('clinic_location')}",
        )
    log.info("Appointment booked %s for user %s", res.inserted_id, user_id)
    return {"appointment_id": str(res.inserted_id), "status": "confirmed"}, 201


def list_appointments(user_id: str, role: str):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    filt = {}
    try:
        if role == "veterinarian":
            # link vet user to doctor by email match
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                doc = db.doctors.find_one({"contact_email": user.get("email")})
                if doc:
                    filt["doctor_id"] = doc["_id"]
        else:
            filt["user_id"] = ObjectId(user_id)
    except InvalidId:
        return {"error": "Invalid user"}, 400
    out = []
    for a in db.appointments.find(filt).sort("scheduled_at", -1):
        out.append(_serialize_appt(db, a))
    return {"appointments": out}, 200


def update_appointment(user_id: str, role: str, appointment_id: str, body: dict):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    try:
        aid = ObjectId(appointment_id)
        uid = ObjectId(user_id)
    except InvalidId:
        return {"error": "Invalid id"}, 400
    appt = db.appointments.find_one({"_id": aid})
    if not appt:
        return {"error": "Appointment not found"}, 404
    if role not in ("admin", "veterinarian") and appt.get("user_id") != uid:
        return {"error": "Forbidden"}, 403
    updates = {"updated_at": utcnow()}
    if "status" in body:
        updates["status"] = body["status"]
    if "scheduled_at" in body:
        dt = _parse_dt(body["scheduled_at"])
        if dt:
            updates["scheduled_at"] = dt
    if "notes" in body:
        updates["notes"] = body["notes"]
    if "treatment_notes" in body and role in ("veterinarian", "admin"):
        updates["treatment_notes"] = body["treatment_notes"]
    db.appointments.update_one({"_id": aid}, {"$set": updates})
    fresh = db.appointments.find_one({"_id": aid})
    return _serialize_appt(db, fresh), 200


def _serialize_appt(db, a):
    doctor = db.doctors.find_one({"_id": a["doctor_id"]})
    user = db.users.find_one({"_id": a["user_id"]})
    return {
        "id": str(a["_id"]),
        "doctor_id": str(a["doctor_id"]),
        "doctor_name": doctor.get("name") if doctor else "",
        "user_id": str(a["user_id"]),
        "user_email": user.get("email") if user else "",
        "scheduled_at": a["scheduled_at"].isoformat() if hasattr(a["scheduled_at"], "isoformat") else str(a["scheduled_at"]),
        "status": a.get("status", "confirmed"),
        "notes": a.get("notes", ""),
        "animal_name": a.get("animal_name", ""),
        "treatment_notes": a.get("treatment_notes", ""),
    }
