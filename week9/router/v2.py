from flask import Blueprint, request, jsonify
from controller.v2 import create_payment, get_payments, update_payment,delete_payment, get_payment

bp = Blueprint('payments_v2', __name__, url_prefix='/api/v2/payments')


# CREATE
@bp.route('/', methods=['POST'])
def create():
    data = request.get_json()
    result, status = create_payment(data)
    return jsonify(result), status


# GET LIST
@bp.route('/', methods=['GET'])
def get_list():
    currency = request.args.get('currency')
    result, status = get_payments(currency)
    return jsonify(result), status


# GET ONE
@bp.route('/<id>', methods=['GET'])
def get_one(id):
    result, status = get_payment(id)
    return jsonify(result), status


# UPDATE
@bp.route('/<id>', methods=['PUT'])
def update(id):
    data = request.get_json()
    result, status = update_payment(id, data)
    return jsonify(result), status


# DELETE
@bp.route('/<id>', methods=['DELETE'])
def delete(id):
    result, status = delete_payment(id)
    return jsonify(result), status