import os

from pymongo import MongoClient, ReturnDocument

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "library_api")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]
books_collection = db["books"]
users_collection = db["users"]
counters_collection = db["counters"]


def books_coll():
    return books_collection


def users_coll():
    return users_collection


def counters_coll():
    return counters_collection


def init_indexes():
    users_collection.create_index("username", unique=True)


def next_book_id() -> int:
    doc = counters_collection.find_one_and_update(
        {"_id": "book"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])


def reset_connection():
    try:
        client.close()
    except Exception:
        pass