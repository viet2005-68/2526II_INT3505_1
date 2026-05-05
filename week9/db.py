from flask_pymongo import PyMongo
from bson import ObjectId

mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)

def serialize_doc(doc):
    return {'_id': str(doc['_id'])} if doc else None

