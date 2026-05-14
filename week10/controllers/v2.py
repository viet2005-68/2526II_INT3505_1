from flask import request, jsonify
from bson import ObjectId
from db import mongo, serialize_doc
from utils.logger import logger

def create_payment():
    data = request.get_json()
    
    logger.info({
        "event": "payment_v2_create_request",
        "body": data,
        "status": "received"
    })

    try:
        # Validate required fields
        if not data:
            logger.error({
                "event": "payment_v2_create_error",
                "error_type": "ValidationError",
                "error": "Request body is empty",
                "status": "failed"
            })
            return jsonify({"error": "Request body cannot be empty"}), 400
        
        if "method" not in data:
            logger.error({
                "event": "payment_v2_create_error",
                "error_type": "ValidationError",
                "error": "Missing required field: method",
                "body": data,
                "status": "failed"
            })
            return jsonify({"error": "Missing required field: method"}), 400
        
        if "amount" not in data:
            logger.error({
                "event": "payment_v2_create_error",
                "error_type": "ValidationError",
                "error": "Missing required field: amount",
                "body": data,
                "status": "failed"
            })
            return jsonify({"error": "Missing required field: amount"}), 400
        
        if "value" not in data["amount"]:
            logger.error({
                "event": "payment_v2_create_error",
                "error_type": "ValidationError",
                "error": "Missing required field: amount.value",
                "body": data,
                "status": "failed"
            })
            return jsonify({"error": "Missing required field: amount.value"}), 400
        
        payment = {
            "method": data["method"],
            "amount": {
                "value": data["amount"]["value"],
                "currency": data["amount"].get("currency", "VND")
            },
            "status": "processing"
        }
        result = mongo.db.payments_v2.insert_one(payment)

        logger.info({
            "event": "payment_v2_created",
            "payment_id": str(result.inserted_id),
            "status": "success"
        })
        
        return jsonify({
            "message": "Created",
            "id": str(result.inserted_id)
        }), 201
    except Exception as e:
        import traceback
        logger.error({
            "event": "payment_v2_create_error",
            "error_type": type(e).__name__,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "body": data,
            "status": "failed"
        })
        raise


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