from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime

mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)

def serialize_doc(doc):
    if not doc:
        return None

    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()  # 🔥 FIX ở đây
        else:
            result[key] = value

    return result

