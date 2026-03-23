from flask import Blueprint
from utils.response import api_response

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["GET"])
def list_users():
    return api_response(data=[], metadata={"resource": "users", "count": 0})
