from flask import request, jsonify

payments_v1 = []


def create_payment():
    data = request.get_json()

    payment = {
        "id": len(payments_v1) + 1,
        "cardNumber": data["cardNumber"],
        "amount": data["amount"]
    }

    payments_v1.append(payment)

    return jsonify(payment), 201


def get_payments():
    return jsonify(payments_v1)


def get_payment(id):
    for payment in payments_v1:
        if payment["id"] == id:
            return jsonify(payment)

    return jsonify({
        "error": "Payment not found"
    }), 404


def update_payment(id):
    data = request.get_json()

    for payment in payments_v1:
        if payment["id"] == id:
            payment["amount"] = data["amount"]

            return jsonify(payment)

    return jsonify({
        "error": "Payment not found"
    }), 404


def delete_payment(id):
    global payments_v1

    payments_v1 = [
        p for p in payments_v1
        if p["id"] != id
    ]

    return jsonify({
        "message": "Deleted"
    })