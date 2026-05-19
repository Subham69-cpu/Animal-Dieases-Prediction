"""Flask application factory and route registration."""
import os
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# Allow running as `python backend/app.py` by putting repo root on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.config import Config
from backend.controllers import (
    animal_controller,
    appointment_controller,
    auth_controller,
    dashboard_controller,
    doctor_controller,
    predict_controller,
    train_controller,
)
from backend.extensions import get_db, init_mongo
from backend.models.db_indexes import ensure_indexes
from backend.utils.jwt_auth import create_token, token_required
from backend.utils.logger import configure_logging
from backend.utils.pdf_report import build_prediction_pdf
from backend.services import model_service


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)
    configure_logging(app.config.get("LOG_LEVEL", "INFO"))
    CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})
    init_mongo(app)
    ensure_indexes(get_db())
    auth_controller.admin_bootstrap(app)

    @app.get("/health")
    def health():
        db = get_db()
        return jsonify(
            {
                "status": "ok",
                "database": "mongo" if db is not None and not getattr(db, "is_sqlite", False) else ("sqlite" if db else "none"),
            }
        )

    @app.post("/signup")
    def signup():
        data, code = auth_controller.signup(request.get_json(force=True, silent=True) or {})
        if code >= 400:
            return jsonify(data), code
        token = create_token(data["user_id"], data["email"], data["role"])
        return jsonify({**data, "token": token}), code

    @app.post("/login")
    def login():
        data, code = auth_controller.login(request.get_json(force=True, silent=True) or {}, app)
        if code >= 400:
            return jsonify(data), code
        return jsonify(data), code

    @app.post("/predict/symptoms")
    @token_required()
    def pred_symptoms():
        uid = getattr(request, "user_id", None)
        out, code = predict_controller.predict_symptoms(app, request.get_json(force=True, silent=True) or {}, uid)
        return jsonify(out), code

    @app.post("/predict/symptoms/demo")
    def pred_symptoms_demo():
        """Open demo without auth (rate-limit in production)."""
        out, code = predict_controller.predict_symptoms(app, request.get_json(force=True, silent=True) or {}, None)
        return jsonify(out), code

    @app.post("/predict/image")
    @token_required()
    def pred_image():
        uid = getattr(request, "user_id", None)
        animal = request.form.get("animal_type", "cow")
        f = request.files.get("image")
        out, code = predict_controller.predict_image(app, f, animal, uid)
        return jsonify(out), code

    @app.post("/predict/image/demo")
    def pred_image_demo():
        animal = request.form.get("animal_type", "cow")
        f = request.files.get("image")
        out, code = predict_controller.predict_image(app, f, animal, None)
        return jsonify(out), code

    @app.post("/predict/hybrid")
    @token_required()
    def pred_hybrid():
        uid = getattr(request, "user_id", None)
        if request.content_type and "application/json" in request.content_type:
            body = request.get_json(force=True, silent=True) or {}
        else:
            body = dict(request.form)
            for k in model_service.SYMPTOM_KEYS:
                if k in body:
                    try:
                        body[k] = int(body[k])
                    except (TypeError, ValueError):
                        body[k] = 0
        f = request.files.get("image")
        out, code = predict_controller.predict_hybrid(app, body, f, uid)
        return jsonify(out), code

    @app.post("/predict/hybrid/demo")
    def pred_hybrid_demo():
        body = dict(request.form)
        for k in model_service.SYMPTOM_KEYS:
            if k in body:
                try:
                    body[k] = int(body[k])
                except (TypeError, ValueError):
                    body[k] = 0
        f = request.files.get("image")
        out, code = predict_controller.predict_hybrid(app, body, f, None)
        return jsonify(out), code

    @app.get("/doctors")
    def doctors():
        q = request.args.get("q")
        species = request.args.get("species")
        out, code = doctor_controller.list_doctors(q, species)
        return jsonify(out), code

    @app.get("/doctor/<doc_id>")
    def doctor(doc_id):
        out, code = doctor_controller.get_doctor(doc_id)
        return jsonify(out), code

    @app.post("/appointment/book")
    @token_required()
    def book():
        out, code = appointment_controller.book_appointment(request.user_id, request.get_json(force=True, silent=True) or {})
        return jsonify(out), code

    @app.get("/appointments")
    @token_required()
    def appts():
        out, code = appointment_controller.list_appointments(request.user_id, request.user_role)
        return jsonify(out), code

    @app.put("/appointment/update")
    @token_required()
    def appt_update():
        body = request.get_json(force=True, silent=True) or {}
        aid = body.get("appointment_id")
        if not aid:
            return jsonify({"error": "appointment_id required"}), 400
        out, code = appointment_controller.update_appointment(request.user_id, request.user_role, aid, body)
        return jsonify(out), code

    @app.put("/appointments/<aid>")
    @token_required()
    def appt_update_rest(aid):
        body = request.get_json(force=True, silent=True) or {}
        out, code = appointment_controller.update_appointment(request.user_id, request.user_role, aid, body)
        return jsonify(out), code

    @app.post("/train/cnn")
    @token_required(["admin"])
    def train_cnn():
        out, code = train_controller.run_cnn_training()
        return jsonify(out), code

    @app.post("/train/ml")
    @token_required(["admin"])
    def train_ml():
        out, code = train_controller.run_ml_training()
        return jsonify(out), code

    @app.get("/dashboard/user")
    @token_required(["user", "admin"])
    def dash_user():
        out, code = dashboard_controller.user_dashboard(request.user_id)
        return jsonify(out), code

    @app.get("/dashboard/doctor")
    @token_required(["veterinarian", "admin"])
    def dash_doc():
        out, code = dashboard_controller.doctor_dashboard(request.user_id, request.user_email or "")
        return jsonify(out), code

    @app.get("/dashboard/admin")
    @token_required(["admin"])
    def dash_admin():
        out, code = dashboard_controller.admin_dashboard()
        return jsonify(out), code

    @app.get("/animals")
    @token_required()
    def animals_get():
        out, code = animal_controller.list_animals(request.user_id)
        return jsonify(out), code

    @app.post("/animals")
    @token_required()
    def animals_post():
        out, code = animal_controller.create_animal(request.user_id, request.get_json(force=True, silent=True) or {})
        return jsonify(out), code

    @app.get("/export/prediction/pdf")
    @token_required()
    def export_pdf():
        """Export most recent prediction as PDF."""
        db = get_db()
        if db is None:
            return jsonify({"error": "Database unavailable"}), 503
        from bson import ObjectId

        try:
            uid = ObjectId(request.user_id)
        except Exception:
            return jsonify({"error": "invalid user"}), 400
        last = db.predictions.find_one({"user_id": uid}, sort=[("created_at", -1)])
        if not last:
            return jsonify({"error": "No predictions to export"}), 404
        last.pop("_id", None)
        last.pop("user_id", None)
        pdf = build_prediction_pdf(last)
        if not pdf:
            return jsonify({"error": "PDF library unavailable. pip install fpdf2"}), 500
        from io import BytesIO

        return send_file(BytesIO(pdf), mimetype="application/pdf", as_attachment=True, download_name="prediction_report.pdf")

    return app
