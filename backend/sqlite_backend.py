"""
Lightweight SQLite persistence when MongoDB is unavailable.
Mimics a small subset of PyMongo collection APIs used by this project.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId


def _json_default(obj: Any):
    if isinstance(obj, ObjectId):
        return {"$oid": str(obj)}
    if isinstance(obj, datetime):
        return {"$date": obj.isoformat()}
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _json_object_hook(d: Any) -> Any:
    if isinstance(d, dict):
        if set(d.keys()) == {"$oid"}:
            return ObjectId(d["$oid"])
        if set(d.keys()) == {"$date"}:
            s = d["$date"]
            if isinstance(s, str):
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
        return {k: _json_object_hook(v) for k, v in d.items()}
    if isinstance(d, list):
        return [_json_object_hook(x) for x in d]
    return d


def _dumps(doc: dict) -> str:
    return json.dumps(doc, default=_json_default)


def _loads(s: str) -> dict:
    return json.loads(s, object_hook=_json_object_hook)


class _InsertOneResult:
    __slots__ = ("inserted_id",)

    def __init__(self, inserted_id: ObjectId):
        self.inserted_id = inserted_id


def _sort_key(doc: dict, key: str):
    v = doc.get(key)
    if isinstance(v, datetime):
        return v.timestamp()
    return v if v is not None else ""


class _Cursor:
    def __init__(self, docs: list[dict]):
        self._docs = docs
        self._sort_spec: list[tuple[str, int]] | None = None
        self._limit_n: int | None = None

    def sort(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            self._sort_spec = list(args[0])
        elif len(args) == 2 and isinstance(args[0], str):
            self._sort_spec = [(args[0], args[1])]
        return self

    def limit(self, n: int):
        self._limit_n = n
        return self

    def __iter__(self):
        docs = list(self._docs)
        if self._sort_spec:
            for key, direction in reversed(self._sort_spec):
                docs.sort(key=lambda d, k=key: _sort_key(d, k), reverse=(direction < 0))
        if self._limit_n is not None:
            docs = docs[: self._limit_n]
        yield from docs


def _oid(value: Any) -> ObjectId | None:
    if value is None:
        return None
    if isinstance(value, ObjectId):
        return value
    try:
        return ObjectId(str(value))
    except InvalidId:
        return None


def _ts(value: Any) -> float:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.timestamp()
    return 0.0


def _match(doc: dict, filt: dict) -> bool:
    if not filt:
        return True
    for k, expected in filt.items():
        if k == "$or":
            return any(_match(doc, part) for part in expected)
        actual = doc.get(k)
        if isinstance(expected, dict) and any(str(sk).startswith("$") for sk in expected.keys()):
            if "$in" in expected:
                arr = expected["$in"]
                if isinstance(actual, list):
                    if not any(x in actual for x in arr):
                        return False
                else:
                    if actual not in arr:
                        return False
            elif "$gte" in expected:
                thr = expected["$gte"]
                if actual is None or _ts(actual) < _ts(thr):
                    return False
            elif "$ne" in expected:
                if actual == expected["$ne"]:
                    return False
        else:
            if k == "_id":
                o1, o2 = _oid(actual), _oid(expected)
                if o1 is not None and o2 is not None:
                    if o1 != o2:
                        return False
                elif actual != expected:
                    return False
            elif k in ("user_id", "doctor_id"):
                o1, o2 = _oid(actual), _oid(expected)
                if o1 is not None and o2 is not None:
                    if o1 != o2:
                        return False
                elif actual != expected:
                    return False
            else:
                if actual != expected:
                    return False
    return True


class _Collection:
    def __init__(self, conn: sqlite3.Connection, name: str, lock: threading.RLock):
        self._conn = conn
        self._name = name
        self._lock = lock

    def create_index(self, *args, **kwargs):
        return None

    def _all(self) -> list[dict]:
        cur = self._conn.execute("SELECT data FROM docs WHERE coll = ?", (self._name,))
        return [_loads(r[0]) for r in cur.fetchall()]

    def find_one(self, filt: dict | None = None, sort: list | None = None) -> dict | None:
        with self._lock:
            docs = [d for d in self._all() if _match(d, filt or {})]
            if sort:
                for key, direction in reversed(sort):
                    docs.sort(key=lambda d, k=key: _sort_key(d, k), reverse=(direction < 0))
            return docs[0] if docs else None

    def find(self, filt: dict | None = None):
        with self._lock:
            docs = [d for d in self._all() if _match(d, filt or {})]
        return _Cursor(docs)

    def insert_one(self, doc: dict) -> _InsertOneResult:
        with self._lock:
            d = dict(doc)
            if "_id" not in d:
                d["_id"] = ObjectId()
            self._conn.execute(
                "INSERT OR REPLACE INTO docs(coll, id, data) VALUES (?,?,?)",
                (self._name, str(d["_id"]), _dumps(d)),
            )
            self._conn.commit()
            return _InsertOneResult(d["_id"])

    def update_one(self, filt: dict, update: dict):
        with self._lock:
            docs = self._all()
            for d in docs:
                if not _match(d, filt):
                    continue
                merged = dict(d)
                for k, v in (update.get("$set") or {}).items():
                    merged[k] = v
                self._conn.execute(
                    "UPDATE docs SET data = ? WHERE coll = ? AND id = ?",
                    (_dumps(merged), self._name, str(merged["_id"])),
                )
                self._conn.commit()
                return
        self._conn.commit()

    def count_documents(self, filt: dict | None = None) -> int:
        with self._lock:
            return sum(1 for d in self._all() if _match(d, filt or {}))

    def estimated_document_count(self) -> int:
        with self._lock:
            cur = self._conn.execute("SELECT COUNT(*) FROM docs WHERE coll = ?", (self._name,))
            return int(cur.fetchone()[0])

    def aggregate(self, pipeline: list):
        """Minimal support for disease trend pipeline."""
        with self._lock:
            if not pipeline:
                return iter(())
            stages = {s.get("$group", {}).get("_id") for s in pipeline if "$group" in s}
            if "$group" in str(pipeline):
                counts: dict[str, int] = {}
                for d in self._all():
                    key = str(d.get("final_prediction") or "unknown")
                    counts[key] = counts.get(key, 0) + 1
                items = [{"_id": k, "count": v} for k, v in counts.items()]
                items.sort(key=lambda x: x["count"], reverse=True)
                for s in pipeline:
                    if "$limit" in s:
                        items = items[: int(s["$limit"])]
                return iter(items)
        return iter(())


class SqliteDatabase:
    """Drop-in replacement for a PyMongo Database object for this app."""

    is_sqlite = True

    def __init__(self, path: str):
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS docs (
                coll TEXT NOT NULL,
                id TEXT NOT NULL,
                data TEXT NOT NULL,
                PRIMARY KEY(coll, id)
            )"""
        )
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_coll ON docs(coll)")
        self._conn.commit()
        self.users = _Collection(self._conn, "users", self._lock)
        self.doctors = _Collection(self._conn, "doctors", self._lock)
        self.appointments = _Collection(self._conn, "appointments", self._lock)
        self.predictions = _Collection(self._conn, "predictions", self._lock)
        self.animals = _Collection(self._conn, "animals", self._lock)
