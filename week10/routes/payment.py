from flask import Blueprint, request, jsonify
from controllers import v1, v2
from utils.limiter import limiter


bp = Blueprint("payments", __name__)


def get_api_version():
    version = request.args.get("v")

    if version:
        return version.replace("v", "")

    return "2"


@bp.route("/", methods=["POST"])
@limiter.limit("10 per minute")
def create_dispatch():
    version = get_api_version()

    if version == "1":
        return v1.create_payment()

    elif version == "2":
        return v2.create_payment()

    return jsonify({
        "error": "Unsupported API version"
    }), 400


@bp.route("/", methods=["GET"])
@limiter.limit("30 per minute")
def list_dispatch():
    version = get_api_version()

    if version == "1":
        return v1.get_payments()

    elif version == "2":
        return v2.get_payments()

    return jsonify({
        "error": "Unsupported API version"
    }), 400


@bp.route("/<int:id>", methods=["GET"])
@limiter.limit("30 per minute")
def get_dispatch(id):
    version = get_api_version()

    if version == "1":
        return v1.get_payment(id)

    elif version == "2":
        return v2.get_payment(id)

    return jsonify({
        "error": "Unsupported API version"
    }), 400


@bp.route("/<int:id>", methods=["PUT"])
def update_dispatch(id):
    version = get_api_version()

    if version == "1":
        return v1.update_payment(id)

    elif version == "2":
        return v2.update_payment(id)

    return jsonify({
        "error": "Unsupported API version"
    }), 400


@bp.route("/<int:id>", methods=["DELETE"])
@limiter.limit("5 per minute")
def delete_dispatch(id):
    version = get_api_version()

    if version == "1":
        return v1.delete_payment(id)

    elif version == "2":
        return v2.delete_payment(id)

    return jsonify({
        "error": "Unsupported API version"
    }), 400