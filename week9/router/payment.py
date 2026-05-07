from flask import Blueprint, request, jsonify, make_response
from controller import v1, v2

bp = Blueprint('payments_unified', __name__)

def get_api_version():
    version = request.args.get('v') or request.args.get('version')
    if not version:
        version = request.headers.get('X-API-Version')
    if version:
        return str(version).lower().replace('v', '')
    return '2'

def add_deprecation_headers(response):
    response.headers['Warning'] = '299 - This API v1 is deprecated. Please migrate to v2.'
    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = 'Wed, 31 Dec 2025 23:59:59 GMT'
    response.headers['Link'] = '</api/v2/payments>; rel="successor-version"'
    return response

def process_v1_response(res):
    if isinstance(res, tuple):
        response = make_response(res[0], res[1])
    else:
        response = make_response(res)
    return add_deprecation_headers(response)

@bp.route('/', methods=['POST'])
def create_dispatch():
    version = get_api_version()
    data = request.get_json()
    if version == '1':
        return process_v1_response(v1.create_payment(data))
    elif version == '2':
        result, status = v2.create_payment(data)
        return jsonify(result), status
    else:
        return jsonify({"error": f"Version {version} not supported"}), 400

@bp.route('/', methods=['GET'])
def get_list_dispatch():
    version = get_api_version()
    if version == '1':
        return process_v1_response(v1.get_all_payments())
    elif version == '2':
        currency = request.args.get('currency')
        result, status = v2.get_payments(currency)
        return jsonify(result), status
    else:
        return jsonify({"error": "Version not supported"}), 400

@bp.route('/<id>', methods=['GET'])
def get_one_dispatch(id):
    version = get_api_version()
    if version == '1':
        return process_v1_response(v1.get_payment(id))
    elif version == '2':
        result, status = v2.get_payment(id)
        return jsonify(result), status
    else:
        return jsonify({"error": "Version not supported"}), 400

@bp.route('/<id>', methods=['PUT'])
def update_dispatch(id):
    version = get_api_version()
    data = request.get_json()
    if version == '1':
        return process_v1_response(v1.update_payment(id, data))
    elif version == '2':
        result, status = v2.update_payment(id, data)
        return jsonify(result), status
    else:
        return jsonify({"error": "Version not supported"}), 400

@bp.route('/<id>', methods=['DELETE'])
def delete_dispatch(id):
    version = get_api_version()
    if version == '1':
        return process_v1_response(v1.delete_payment(id))
    elif version == '2':
        result, status = v2.delete_payment(id)
        return jsonify(result), status
    else:
        return jsonify({"error": "Version not supported"}), 400
