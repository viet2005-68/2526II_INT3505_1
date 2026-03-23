from flask import Blueprint, jsonify

loans_bp = Blueprint("loans", __name__, url_prefix="/loans")


@loans_bp.route("", methods=["GET"])
def list_loans():
    return jsonify([])
