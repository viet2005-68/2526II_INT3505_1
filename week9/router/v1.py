from flask import Blueprint, request, jsonify
from controller.v1 import create_payment, get_all_payments, get_payment, update_payment, delete_payment

v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

@v1_bp.route('/', methods=['POST'])
def create():
    data = request.get_json()
    return create_payment(data)

@v1_bp.route('/', methods=['GET'])
def get_all():
    return get_all_payments()

@v1_bp.route('/<id>', methods=['GET'])
def get_payment_route(id):
    return get_payment(id)

@v1_bp.route('/<id>', methods=['PUT'])
def update_payment_route(id):
    data = request.get_json()
    return update_payment(id, data)

@v1_bp.route('/<id>', methods=['DELETE'])
def delete_payment_route(id):
    return delete_payment(id)

@v1_bp.after_request
def add_deprecation_headers(response):
    response.headers['Warning'] = '299 - This API v1 is deprecated. Please migrate to v2.'
    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = 'Wed, 31 Dec 2025 23:59:59 GMT'
    response.headers['Link'] = '</api/v2/payments>; rel="successor-version"'
    return response
