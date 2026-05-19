"""Build prediction API payloads and persist history."""
import logging
from typing import Any

from ..extensions import get_db
from ..models.db_indexes import utcnow
from ..services import model_service
from ..utils.disease_knowledge import lookup_disease

log = logging.getLogger(__name__)

ALLOWED_ANIMALS = {"cow", "dog", "cat", "goat", "poultry"}


def _severity_from_conf(conf: float | None, default: str) -> str:
    if conf is None:
        return default
    if conf >= 0.85:
        return "High" if default != "Critical" else "Critical"
    if conf >= 0.6:
        return "Medium"
    return "Low"


def build_prediction_record(
    animal_type: str,
    disease: str,
    cnn_conf: float | None,
    ml_conf: float | None,
    final_conf: float | None,
    final_label: str,
    recommended_action: str,
) -> dict[str, Any]:
    info = lookup_disease(final_label)
    sev = info.get("severity_default", "Unknown")
    if final_conf is not None:
        sev = _severity_from_conf(final_conf, sev)
    return {
        "animal_type": animal_type,
        "disease": disease,
        "final_prediction": final_label,
        "cnn_confidence": cnn_conf,
        "ml_confidence": ml_conf,
        "final_confidence": final_conf,
        "severity": sev,
        "precautions": info.get("precautions", []),
        "treatment": info.get("treatment", ""),
        "vet_recommendation": info.get("vet_recommendation", ""),
        "recommended_action": recommended_action,
    }


def predict_symptoms(app, body: dict, user_id: str | None) -> tuple[dict, int]:
    animal = (body.get("animal_type") or "").strip().lower()
    if animal not in ALLOWED_ANIMALS:
        return {"error": f"animal_type must be one of {sorted(ALLOWED_ANIMALS)}"}, 400
    sym = {k: int(body.get(k, 0)) for k in model_service.SYMPTOM_KEYS}
    label, conf = model_service.predict_symptom_ml(app, animal, sym)
    if label is None:
        return {
            "error": "Symptom ML model not loaded. Run: python scripts/train_ml.py",
            "hint": "Train models after generating the dataset.",
        }, 503
    rec = build_prediction_record(
        animal, label, None, conf, conf, label, "Consider imaging if skin or visible signs present."
    )
    _save_prediction(user_id, rec, mode="symptoms")
    return rec, 200


def predict_image(app, file_storage, animal_type: str, user_id: str | None) -> tuple[dict, int]:
    animal = (animal_type or "").strip().lower()
    if animal not in ALLOWED_ANIMALS:
        return {"error": f"animal_type must be one of {sorted(ALLOWED_ANIMALS)}"}, 400
    if not file_storage or not file_storage.filename:
        return {"error": "Image file required"}, 400
    raw = file_storage.read()
    label, conf = model_service.predict_cnn(app, raw)
    if label is None:
        return {
            "error": "CNN model not loaded. Run: python scripts/train_cnn.py",
        }, 503
    rec = build_prediction_record(
        animal,
        label,
        conf,
        None,
        conf,
        label,
        "Correlate with clinical signs and laboratory tests.",
    )
    _save_prediction(user_id, rec, mode="image")
    return rec, 200


def predict_hybrid(app, body: dict, file_storage, user_id: str | None) -> tuple[dict, int]:
    animal = (body.get("animal_type") or "").strip().lower()
    if animal not in ALLOWED_ANIMALS:
        return {"error": f"animal_type must be one of {sorted(ALLOWED_ANIMALS)}"}, 400
    sym = {k: int(body.get(k, 0)) for k in model_service.SYMPTOM_KEYS}
    ml_label, ml_conf = model_service.predict_symptom_ml(app, animal, sym)
    if ml_label is None:
        return {
            "error": "Symptom ML model not loaded. Run: python scripts/train_ml.py",
        }, 503
    cnn_label, cnn_conf = (None, None)
    if file_storage and file_storage.filename:
        raw = file_storage.read()
        cnn_label, cnn_conf = model_service.predict_cnn(app, raw)
    final_label, final_conf, action = model_service.hybrid_combine(
        cnn_label, cnn_conf, ml_label, ml_conf
    )
    rec = build_prediction_record(
        animal,
        final_label,
        cnn_conf,
        ml_conf,
        final_conf,
        final_label,
        action,
    )
    rec["cnn_prediction"] = cnn_label
    rec["ml_prediction"] = ml_label
    _save_prediction(user_id, rec, mode="hybrid")
    return rec, 200


def _save_prediction(user_id: str | None, record: dict, mode: str):
    db = get_db()
    if db is None or not user_id:
        return
    try:
        from bson import ObjectId

        oid = ObjectId(user_id)
    except Exception:
        return
    doc = {**record, "user_id": oid, "mode": mode, "created_at": utcnow()}
    db.predictions.insert_one(doc)
    log.debug("Prediction saved for user %s mode=%s", user_id, mode)
