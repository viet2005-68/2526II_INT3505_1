from flask import Blueprint
from utils.response import api_response

loans_bp = Blueprint("loans", __name__, url_prefix="/loans")


@loans_bp.route("", methods=["GET"])
def list_loans():
    return api_response(data=[], metadata={"resource": "loans", "count": 0})
