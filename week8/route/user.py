from flask import Blueprint, request
from utils.response import api_error, api_response
from database import db
from models import User
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
def list_users():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    users = db.session.query(User).offset((page - 1) * per_page).limit(per_page).all()
    data = []
    for user in users:
        data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        })
    return api_response(data=data, metadata={"resource": "users", "count": len(data), "page": page, "per_page": per_page})


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return api_error("User not found", status_code=404)
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
    return api_response(data=data, metadata={"resource": "user"})

@users_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data.get("username") or not data.get("email") or not data.get("password"):
        return api_error("Username, email, and password are required", status_code=400)
    
    if db.session.query(User).filter_by(username=data["username"]).first():
        return api_error("Username already exists", status_code=400)
    
    if db.session.query(User).filter_by(email=data["email"]).first():
        return api_error("Email already exists", status_code=400)

    user = User(username=data["username"], email=data["email"], password=data["password"])
    db.session.add(user)
    db.session.commit()

    return api_response(data={"id": user.id}, metadata={"resource": "user"}, status_code=201)