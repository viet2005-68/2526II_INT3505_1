from flask import request, jsonify
from bson import ObjectId
from db import mongo, serialize_doc


def create_payment():
    data = request.get_json()

    payment = {
        "method": data["method"],
        "amount": {
            "value": data["amount"]["value"],
            "currency": data["amount"].get("currency", "VND")
        },
        "status": "processing"
    }

    result = mongo.db.payments_v2.insert_one(payment)

    return jsonify({
        "message": "Created",
        "id": str(result.inserted_id)
    }), 201


def get_payments():
    payments = mongo.db.payments_v2.find()

    return jsonify([
        serialize_doc(p)
        for p in payments
    ])


def get_payment(id):
    try:
        payment = mongo.db.payments_v2.find_one({
            "_id": ObjectId(id)
        })

    except:
        return jsonify({
            "error": "Invalid ID"
        }), 400

    if not payment:
        return jsonify({
            "error": "Payment not found"
        }), 404

    return jsonify(
        serialize_doc(payment)
    )


def update_payment(id):
    data = request.get_json()

    update_data = {}

    if "status" in data:
        update_data["status"] = data["status"]

    try:
        result = mongo.db.payments_v2.update_one(
            {
                "_id": ObjectId(id)
            },
            {
                "$set": update_data
            }
        )

    except:
        return jsonify({
            "error": "Invalid ID"
        }), 400

    if not result.matched_count:
        return jsonify({
            "error": "Payment not found"
        }), 404

    return jsonify({
        "message": "Updated"
    })


def delete_payment(id):
    try:
        result = mongo.db.payments_v2.update_one(
            {
                "_id": ObjectId(id)
            },
            {
                "$set": {
                    "status": "archived"
                }
            }
        )

    except:
        return jsonify({
            "error": "Invalid ID"
        }), 400

    if not result.matched_count:
        return jsonify({
            "error": "Payment not found"
        }), 404

    return jsonify({
        "message": "Soft deleted"
    })