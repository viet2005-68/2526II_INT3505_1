from flask import request, jsonify
from bson import ObjectId
from db import mongo, serialize_doc


def create_payment():
    data = request.get_json()

    payment = {
        "cardNumber": data["cardNumber"],
        "amount": data["amount"]
    }

    result = mongo.db.payments_v1.insert_one(payment)

    return jsonify({
        "message": "Created",
        "id": str(result.inserted_id)
    }), 201


def get_payments():
    payments = mongo.db.payments_v1.find()

    return jsonify([
        serialize_doc(p)
        for p in payments
    ])


def get_payment(id):
    try:
        payment = mongo.db.payments_v1.find_one({
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

    try:
        result = mongo.db.payments_v1.update_one(
            {
                "_id": ObjectId(id)
            },
            {
                "$set": {
                    "amount": data["amount"]
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
        "message": "Updated"
    })


def delete_payment(id):
    try:
        result = mongo.db.payments_v1.delete_one({
            "_id": ObjectId(id)
        })

    except:
        return jsonify({
            "error": "Invalid ID"
        }), 400

    if not result.deleted_count:
        return jsonify({
            "error": "Payment not found"
        }), 404

    return jsonify({
        "message": "Deleted"
    })