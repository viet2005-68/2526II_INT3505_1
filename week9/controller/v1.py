from bson import ObjectId
from flask import jsonify

from db import mongo, serialize_doc
from datetime import datetime

def create_payment(data):
    required_fields = ['cardNumber', 'amount']
    if not all(field in data for field in required_fields):
        return {'error': 'missing required field: cardNumber, amount'}, 400

    payment_record = {
        'cardNumber': data['cardNumber'],
        'amount': data['amount'],
        'status': "pending",
        "created_at": datetime.utcnow()  # sửa typo luôn
    }

    result = mongo.db.payments.insert_one(payment_record)

    return {
        'id': str(result.inserted_id),  # nhớ convert ObjectId
        'message': 'payment created'
    }, 201

def get_payment(id):
    try:
        payments = mongo.db.payments.find_one({'_id': ObjectId(id)})
    except:
        return {'error': 'service is unavailable, please try again'}, 404

    if payments is None:
        return {'error': 'payment not found'}, 404
    return jsonify(serialize_doc(payments)), 200

def get_all_payments():
    try:
        payments = mongo.db.payments.find()
    except:
        return {'error': 'service is unavailable, please try again'}, 404
    return jsonify([serialize_doc(doc) for doc in payments]), 200

def update_payment(id, data):
    required_fields = ['cardNumber', 'amount']
    if not all(field in data for field in required_fields):
        return {'error': 'missing required field: cardNumber, amount'}, 400
    payment_record = {
        'cardNumber': data['cardNumber'],
        'amount': data['amount']
    }

    try:
        result = mongo.db.payments.update_one({"_id": ObjectId(id)}, {'$set': payment_record})
    except:
        return {'error': 'Invalid id'}, 404

    if result.matched_count:
        return {'message': 'payment updated'}, 200

    return {'message': 'Not founded'}, 404

def delete_payment(id):
    try:
        result = mongo.db.payments.delete_one({'_id': ObjectId(id)})
    except:
        return {"error": "Not found"}, 404

    if result.deleted_count:
        return {'message': 'payment deleted'}, 200
    return {'message': 'Not found'}, 404