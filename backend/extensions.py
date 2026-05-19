"""Shared extension instances (MongoDB client)."""
from pathlib import Path

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from .config import Config
from .sqlite_backend import SqliteDatabase

mongo_client: MongoClient | None = None
mongo_db = None


def init_mongo(app):
    """Initialize MongoDB; on failure optionally use SQLite so signup works without Mongo."""
    global mongo_client, mongo_db
    mongo_client = None
    mongo_db = None
    uri = app.config.get("MONGO_URI", Config.MONGO_URI)
    try:
        mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command("ping")
        db_name = app.config.get("MONGO_DB_NAME", Config.MONGO_DB_NAME)
        mongo_db = mongo_client[db_name]
        app.logger.info("MongoDB connected.")
    except PyMongoError as e:
        app.logger.warning("MongoDB unavailable: %s", e)
        mongo_client = None
        mongo_db = None
        if app.config.get("USE_SQLITE_FALLBACK", Config.USE_SQLITE_FALLBACK):
            path = app.config.get("SQLITE_PATH", Config.SQLITE_PATH)
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            mongo_db = SqliteDatabase(path)
            app.logger.warning("Using SQLite fallback at %s (register/login work locally).", path)


def get_db():
    return mongo_db
