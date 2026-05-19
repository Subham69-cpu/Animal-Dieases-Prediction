"""Doctor listing and profiles (MongoDB + seed)."""
import logging

from bson import ObjectId
from bson.errors import InvalidId

from ..extensions import get_db
from ..models.db_indexes import utcnow

log = logging.getLogger(__name__)

DEFAULT_DOCTORS = [
    {
        "name": "Dr. Ananya Sharma",
        "specialization": "Large Animal / Dairy",
        "experience_years": 12,
        "clinic_location": "Rural Veterinary Center, Sector 4",
        "available_timings": ["Mon–Fri 09:00–17:00", "Sat 09:00–13:00"],
        "contact_email": "ananya.sharma@clinic.example",
        "contact_phone": "+91-90000-10001",
        "consultation_fee_inr": 800,
        "rating_avg": 4.8,
        "review_count": 124,
        "species_focus": ["cow", "goat"],
    },
    {
        "name": "Dr. Marcus Lee",
        "specialization": "Small Animal Surgery",
        "experience_years": 9,
        "clinic_location": "City Pet Hospital, Downtown",
        "available_timings": ["Mon–Sat 10:00–20:00"],
        "contact_email": "marcus.lee@clinic.example",
        "contact_phone": "+91-90000-10002",
        "consultation_fee_inr": 1200,
        "rating_avg": 4.9,
        "review_count": 342,
        "species_focus": ["dog", "cat"],
    },
    {
        "name": "Dr. Priya Nair",
        "specialization": "Avian & Poultry Health",
        "experience_years": 15,
        "clinic_location": "Poultry Health Unit, Agri Zone",
        "available_timings": ["Mon–Fri 08:00–16:00"],
        "contact_email": "priya.nair@clinic.example",
        "contact_phone": "+91-90000-10003",
        "consultation_fee_inr": 600,
        "rating_avg": 4.7,
        "review_count": 89,
        "species_focus": ["poultry"],
    },
]


def seed_doctors_if_empty():
    db = get_db()
    if db is None:
        return
    if db.doctors.estimated_document_count() > 0:
        return
    for d in DEFAULT_DOCTORS:
        d["created_at"] = utcnow()
        db.doctors.insert_one(d)
    log.info("Seeded default veterinarians.")


def list_doctors(query: str | None, species: str | None):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    seed_doctors_if_empty()
    filt = {}
    if species:
        filt["species_focus"] = {"$in": [species.strip().lower()]}
    cur = db.doctors.find(filt)
    items = []
    for doc in cur:
        items.append(_serialize_doctor(doc))
    if query:
        q = query.lower()
        items = [x for x in items if q in x["name"].lower() or q in x.get("specialization", "").lower()]
    return {"doctors": items}, 200


def get_doctor(doctor_id: str):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}, 503
    try:
        oid = ObjectId(doctor_id)
    except InvalidId:
        return {"error": "Invalid doctor id"}, 400
    doc = db.doctors.find_one({"_id": oid})
    if not doc:
        return {"error": "Doctor not found"}, 404
    return _serialize_doctor(doc), 200


def _serialize_doctor(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name"),
        "specialization": doc.get("specialization"),
        "experience_years": doc.get("experience_years"),
        "clinic_location": doc.get("clinic_location"),
        "available_timings": doc.get("available_timings", []),
        "contact_email": doc.get("contact_email"),
        "contact_phone": doc.get("contact_phone"),
        "consultation_fee_inr": doc.get("consultation_fee_inr"),
        "rating_avg": doc.get("rating_avg"),
        "review_count": doc.get("review_count"),
        "species_focus": doc.get("species_focus", []),
    }
