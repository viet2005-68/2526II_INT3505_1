"""MongoDB connection helpers (simple singleton; optional mongomock for tests)."""
import os
from typing import Optional

from pymongo import ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.environ.get("MONGODB_DB", "library_api")

_client = None  # type: ignore
_db: Optional[Database] = None


def reset_connection() -> None:
    global _client, _db
    if _client is not None:
        try:
            _client.close()
        except Exception:
            pass
    _client = None
    _db = None


def get_client():
    global _client
    if _client is None:
        if os.environ.get("USE_MONGOMOCK"):
            import mongomock

            _client = mongomock.MongoClient()
        else:
            from pymongo import MongoClient

            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_db() -> Database:
    global _db
    if _db is None:
        _db = get_client()[MONGODB_DB]
    return _db


def books_coll() -> Collection:
    return get_db()["books"]


def users_coll() -> Collection:
    return get_db()["users"]


def counters_coll() -> Collection:
    return get_db()["counters"]


def init_indexes() -> None:
    try:
        users_coll().create_index("username", unique=True)
    except PyMongoError:
        raise


def next_book_id() -> int:
    doc = counters_coll().find_one_and_update(
        {"_id": "book"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])
