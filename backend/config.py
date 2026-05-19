"""Application configuration loaded from environment variables."""
import os
from pathlib import Path
from datetime import timedelta


class Config:
    """Base configuration for Flask and external services."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me-in-production")
    JWT_SECRET = os.environ.get("JWT_SECRET", SECRET_KEY)
    JWT_EXPIRATION = timedelta(hours=int(os.environ.get("JWT_EXPIRE_HOURS", "24")))

    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/vet_healthcare")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "vet_healthcare")

    # When MongoDB is down, store users/appointments locally (dev-friendly).
    USE_SQLITE_FALLBACK = os.environ.get("USE_SQLITE_FALLBACK", "true").lower() == "true"
    SQLITE_PATH = os.environ.get(
        "SQLITE_PATH",
        str(Path(__file__).resolve().parent.parent / "data" / "vet_local.db"),
    )

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

    CNN_MODEL_PATH = os.environ.get("CNN_MODEL_PATH", os.path.join(os.path.dirname(__file__), "..", "cnn_model", "model.h5"))
    ML_MODEL_DIR = os.environ.get("ML_MODEL_DIR", os.path.join(os.path.dirname(__file__), "..", "ml_model"))

    DATASET_ROOT = os.environ.get("DATASET_ROOT", os.path.join(os.path.dirname(__file__), "..", "dataset"))

    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM = os.environ.get("SMTP_FROM", "noreply@vethealth.local")
    EMAIL_ENABLED = os.environ.get("EMAIL_ENABLED", "false").lower() == "true"

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
