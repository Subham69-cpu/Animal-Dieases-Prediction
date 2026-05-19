"""Load CNN (Keras) and symptom ML (sklearn Pipeline) lazily."""
import json
import logging
import os

import joblib
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

_cnn_model = None
_ml_pipeline = None
_cnn_class_indices = None


def reset_caches():
    """Clear loaded models after retraining."""
    global _cnn_model, _ml_pipeline, _cnn_class_indices
    _cnn_model = None
    _ml_pipeline = None
    _cnn_class_indices = None


def get_cnn_model(app):
    global _cnn_model, _cnn_class_indices
    if _cnn_model is not None:
        return _cnn_model, _cnn_class_indices
    path = app.config.get("CNN_MODEL_PATH")
    if not path or not os.path.isfile(path):
        log.warning("CNN model not found at %s. Run training script.", path)
        return None, None
    try:
        import tensorflow as tf

        _cnn_model = tf.keras.models.load_model(path)
        labels_path = os.path.join(os.path.dirname(path), "class_indices.json")
        if os.path.isfile(labels_path):
            with open(labels_path, "r", encoding="utf-8") as f:
                _cnn_class_indices = json.load(f)
        else:
            _cnn_class_indices = {}
        log.info("Loaded CNN model from %s", path)
        return _cnn_model, _cnn_class_indices
    except Exception as e:
        log.exception("Failed to load CNN: %s", e)
        return None, None


def get_ml_pipeline(app):
    global _ml_pipeline
    if _ml_pipeline is not None:
        return _ml_pipeline
    d = app.config.get("ML_MODEL_DIR")
    path = os.path.join(d, "symptom_pipeline.joblib")
    if not os.path.isfile(path):
        log.warning("ML pipeline not found at %s", path)
        return None
    try:
        _ml_pipeline = joblib.load(path)
        log.info("Loaded ML symptom pipeline.")
        return _ml_pipeline
    except Exception as e:
        log.exception("Failed to load ML pipeline: %s", e)
        return None


def predict_cnn(app, image_bytes: bytes) -> tuple[str | None, float | None]:
    """Return (disease_label, confidence) from image bytes."""
    import cv2

    model, class_indices = get_cnn_model(app)
    if model is None:
        return None, None
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None, None
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    target = model.input_shape[1:3]
    if target[0] and target[1]:
        img = cv2.resize(img, (int(target[1]), int(target[0])))
    batch = np.expand_dims(img / 255.0, axis=0)
    probs = model.predict(batch, verbose=0)[0]
    idx = int(np.argmax(probs))
    conf = float(probs[idx])
    inv = {int(v): k for k, v in class_indices.items()} if class_indices else {}
    label = inv.get(idx, str(idx))
    raw = label
    if "__" in raw:
        label = raw.split("__", 1)[1]
    return label.replace("_", " ").title(), conf


SYMPTOM_KEYS = [
    "fever",
    "cough",
    "vomiting",
    "diarrhea",
    "skin_problem",
    "breathing_issue",
    "appetite_loss",
    "weakness",
]


def predict_symptom_ml(app, animal_type: str, symptoms: dict) -> tuple[str | None, float | None]:
    """Run sklearn pipeline on one row."""
    pipe = get_ml_pipeline(app)
    if pipe is None:
        return None, None
    row = {"animal_type": animal_type}
    for k in SYMPTOM_KEYS:
        row[k] = int(symptoms.get(k, 0))
    X = pd.DataFrame([row])
    if hasattr(pipe, "predict_proba"):
        proba = pipe.predict_proba(X)[0]
        idx = int(np.argmax(proba))
        clf = pipe.named_steps.get("clf", pipe)
        classes = list(getattr(clf, "classes_", []))
        if not classes:
            return None, None
        label = classes[idx]
        conf = float(proba[idx])
        return str(label).replace("_", " ").title(), conf
    pred = pipe.predict(X)[0]
    return str(pred).replace("_", " ").title(), None


def hybrid_combine(cnn_label, cnn_conf, ml_label, ml_conf, weights=(0.55, 0.45)):
    """Weighted disease selection; boost when both agree."""
    w_cnn, w_ml = weights
    if cnn_label is None and ml_label is None:
        return "Unknown", 0.0, "Book veterinary appointment for examination."
    if cnn_label is None:
        return ml_label, ml_conf or 0.0, "Based primarily on symptoms; imaging recommended if signs persist."
    if ml_label is None:
        return cnn_label, cnn_conf or 0.0, "Based primarily on image analysis; confirm with clinical signs."
    n_cnn = cnn_label.lower().replace(" ", "_")
    n_ml = ml_label.lower().replace(" ", "_")
    agree = n_cnn == n_ml or n_cnn in n_ml or n_ml in n_cnn
    base = w_cnn * (cnn_conf or 0) + w_ml * (ml_conf or 0)
    if agree:
        base = min(0.99, base + 0.08)
        final_label = cnn_label
    else:
        # pick higher weighted branch
        score_cnn = w_cnn * (cnn_conf or 0)
        score_ml = w_ml * (ml_conf or 0)
        final_label = cnn_label if score_cnn >= score_ml else ml_label
    action = (
        "Book veterinary appointment immediately."
        if base >= 0.75
        else "Schedule a veterinary check-up to confirm diagnosis."
    )
    return final_label, float(base), action
