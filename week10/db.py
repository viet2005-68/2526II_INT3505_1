from flask_pymongo import PyMongo

mongo = PyMongo()


def init_db(app):
    mongo.init_app(app)


def serialize_doc(doc):
    if not doc:
        return None

    doc["_id"] = str(doc["_id"])

    return doc