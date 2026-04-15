import connexion
from typing import Tuple

from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash

from openapi_server import mongo
from openapi_server.auth_tokens import create_access_token
from openapi_server.models.error import Error
from openapi_server.models.login_payload import LoginPayload
from openapi_server.models.login_response import LoginResponse
from openapi_server.models.message_response import MessageResponse
from openapi_server.models.register_payload import RegisterPayload


def _err(message: str, code: int) -> Tuple[Error, int]:
    return Error(error=message), code


def api_auth_login_post(body):
    login_payload = body
    if connexion.request.is_json:
        login_payload = LoginPayload.from_dict(connexion.request.get_json())

    if not login_payload.username or not login_payload.password:
        return _err("username and password are required", 400)

    try:
        doc = mongo.users_coll().find_one({"username": login_payload.username})
    except PyMongoError:
        return _err("Database error", 500)

    if not doc or not check_password_hash(doc["password_hash"], login_payload.password):
        return _err("Invalid username or password", 401)

    token = create_access_token(login_payload.username)
    return LoginResponse(access_token=token, token_type="Bearer"), 200


def api_auth_register_post(body):
    register_payload = body
    if connexion.request.is_json:
        register_payload = RegisterPayload.from_dict(connexion.request.get_json())

    if not register_payload.username or not register_payload.password:
        return _err("username and password are required", 400)
    if len(register_payload.password) < 6:
        return _err("password must be at least 6 characters", 400)

    doc = {
        "username": register_payload.username,
        "password_hash": generate_password_hash(register_payload.password),
    }
    try:
        mongo.users_coll().insert_one(doc)
    except DuplicateKeyError:
        return _err("Username already taken", 400)
    except PyMongoError:
        return _err("Database error", 500)

    return MessageResponse(message="User registered successfully"), 201
