from datetime import datetime
from bson import ObjectId
from db import mongo, serialize_doc


# CREATE
def create_payment(data):
    if 'method' not in data or 'amount' not in data:
        return {"error": "missing method or amount object"}, 400

    payment_record = {
        "method": data['method'],
        "amount": {
            "value": data['amount'].get('value'),
            "currency": data['amount'].get('currency', 'VND')
        },
        "details": data.get('details', {}),
        "status": 'pending',
        "created_at": datetime.utcnow(),
    }

    result = mongo.db.payments_v2.insert_one(payment_record)

    return {
        "message": "Payment created successfully",
        "id": str(result.inserted_id),
        "data": serialize_doc(payment_record)
    }, 201


# GET LIST
def get_payments(currency=None):
    query = {}

    if currency:
        query['amount.currency'] = currency

    payments = mongo.db.payments_v2.find(query).limit(20)

    return {
        "count": mongo.db.payments_v2.count_documents(query),
        "items": [serialize_doc(doc) for doc in payments]
    }, 200


# GET ONE
def get_payment(id):
    try:
        payment = mongo.db.payments_v2.find_one({"_id": ObjectId(id)})
    except:
        return {"error": "Invalid ID format"}, 400

    if not payment:
        return {"error": "Payment not found"}, 404

    return serialize_doc(payment), 200


# UPDATE
def update_payment(id, data):
    if 'amount' in data:
        return {"error": "Cannot modify amount"}, 403

    update_data = {}

    if 'status' in data:
        update_data['status'] = data['status']

    if 'details' in data:
        update_data['details'] = data['details']

    try:
        result = mongo.db.payments_v2.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
    except:
        return {"error": "Invalid ID"}, 400

    if result.matched_count:
        return {"message": "Updated successfully"}, 200

    return {"error": "Not found"}, 404


# DELETE (soft delete)
def delete_payment(id):
    try:
        result = mongo.db.payments_v2.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "status": "archived",
                    "deleted_at": datetime.utcnow()
                }
            }
        )
    except:
        return {"error": "Invalid ID"}, 400

    if result.matched_count:
        return {"message": "Payment archived"}, 200

    return {"error": "Not found"}, 404