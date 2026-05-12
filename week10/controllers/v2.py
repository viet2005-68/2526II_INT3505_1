from flask import request, jsonify

payments_v2 = []


def create_payment():
    data = request.get_json()

    payment = {
        "id": len(payments_v2) + 1,
        "method": data["method"],
        "amount": {
            "value": data["amount"]["value"],
            "currency": data["amount"].get("currency", "VND")
        },
        "status": "processing"
    }

    payments_v2.append(payment)

    return jsonify(payment), 201


def get_payments():
    return jsonify(payments_v2)


def get_payment(id):
    for payment in payments_v2:
        if payment["id"] == id:
            return jsonify(payment)

    return jsonify({
        "error": "Payment not found"
    }), 404


def update_payment(id):
    data = request.get_json()

    for payment in payments_v2:
        if payment["id"] == id:

            if "status" in data:
                payment["status"] = data["status"]

            return jsonify(payment)

    return jsonify({
        "error": "Payment not found"
    }), 404


def delete_payment(id):
    for payment in payments_v2:
        if payment["id"] == id:
            payment["status"] = "archived"

            return jsonify({
                "message": "Soft deleted"
            })

    return jsonify({
        "error": "Payment not found"
    }), 404