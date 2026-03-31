from functools import wraps
import re

from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import jwt
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["JWT_ACCESS_SECRET"] = os.getenv("JWT_ACCESS_SECRET", "dev-access-secret-key-change-in-production")
app.config["JWT_REFRESH_SECRET"] = os.getenv("JWT_REFRESH_SECRET", "dev-refresh-secret-key-change-in-production")
ACCESS_MIN = int(os.getenv('ACCESS_MIN', '15'))
REFRESH_DAYS = int(os.getenv('REFRESH_DAYS', '7'))



USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password_hash": generate_password_hash("admin123"),
        "role": "admin",
        "email": "admin@example.com",
        "name": "Administrator",
        "active": True
    },
    "user1": {
        "id": 2,
        "username": "user1",
        "password_hash": generate_password_hash("user123"),
        "role": "user",
        "email": "user1@example.com",
        "name": "John Doe",
        "active": True
    }
}

REFRESH_STORE = {}
REVOKED_ACCESS = set()
def _now():
    return datetime.now(timezone.utc)
@app.route("/")
def index():
    return "Hello, World!"

def create_access_token(user):
    role = user['role']
    now = _now()
    scopes = [] 
    if role == "admin": 
        scopes = ["read:users", "write:users", "delete:users", "read:profile"] 
    elif role == "user": 
        scopes = ["read:profile"]
    payload = {
        'sub': user['id'],
        'usr': user['username'],
        'role': user['role'],
        'scopes': scopes,
        'type': 'access',
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=ACCESS_MIN)).timestamp()),
    }
    return jwt.encode(payload, app.config['JWT_ACCESS_SECRET'], algorithm='HS256')

def _is_email_valid(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def _validate_password(pw: str):
    if len(pw) < 8:
        return False, "Password must be >= 8 chars"
    if not re.search(r'[A-Z]', pw): return False, "Requires uppercase"
    if not re.search(r'[a-z]', pw): return False, "Requires lowercase"
    if not re.search(r'\d', pw): return False, "Requires a number"
    return True, ""

def create_refresh_token(user):
    tid = secrets.token_hex(16)
    now = _now()
    expires_at = now + timedelta(days=REFRESH_DAYS)
    payload = {
        'sub': user['id'],
        'usr': user['username'],
        'type': 'refresh',
        'tid': tid,
        'exp': int(expires_at.timestamp()),
    }
    token = jwt.encode(payload, app.config['JWT_REFRESH_SECRET'], algorithm='HS256')
    REFRESH_STORE[tid] = {
        'user_id': user['id'],
        'created_at': now,
        'expires_at': expires_at
    }
    return token

def decode_access_token(token):
    try:
        if token in REVOKED_ACCESS:
            return None 
        data = jwt.decode(token, app.config['JWT_ACCESS_SECRET'], algorithms=['HS256'])
        if data.get('type') != 'access':
            return None
        return data
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def require_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        data = decode_access_token(token)
        if not data:
            return jsonify({"error": "Invalid or expired token"}), 401
        username = data.get('usr')
        user = USERS.get(username)
        if not user or not user['active']:
            return jsonify({"error": "User not found or inactive"}), 401
        user_copy = user.copy()
        user_copy['scopes'] = data.get('scopes', [])
        request.user = user_copy
        return fn(*args, **kwargs)
    return wrapper

def require_admin(fn):
    @wraps(fn)
    @require_token
    def wrapper(*args, **kwargs):
        if request.user['role'] != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        return fn(*args, **kwargs)
    return wrapper

def require_scopes(required_scopes):
    def decorator(fn):
        @wraps(fn)
        @require_token
        def wrapper(*args, **kwargs):
            token_scopes = request.user.get('scopes', [])
            if required_scopes not in token_scopes:
                return jsonify({"error": "Insufficient scope"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def decode_refresh_token(token):
    try:
        data = jwt.decode(token, app.config['JWT_REFRESH_SECRET'], algorithms=['HS256'])
        if data.get('type') != 'refresh':
            return None
        tid = data.get('tid')
        if not tid or tid not in REFRESH_STORE:
            return None
        return data
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

@app.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json() or {}
    rt = data.get('refresh_token')
    if not rt:
        return jsonify({"error": "refresh_token_required"}),400
    payload = decode_refresh_token(rt)
    if not payload:
        return jsonify({"error": "invalid_or_expired_refresh"}), 401
    username = payload.get('usr')
    user = USERS.get(username)
    if not user or not user['active']:
        return jsonify({"error": "user_inactive"}), 401
    
    new_access = create_access_token(user)
    return jsonify({
        "access_token": new_access,
        "token_type": "Bearer",
        "expires_in": ACCESS_MIN * 60
    }), 200

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")
    name = data.get("name", "")

    if not username or not email or not password or not name:
        return jsonify({"error": "All fields are required"}), 400

    if not _is_email_valid(email):
        return jsonify({"error": "Invalid email format"}), 400
    for u in USERS.values():
        if u["email"] == email:
            return jsonify({"error": "Email already exists"}), 400
    if USERS.get(username):
        return jsonify({"error": "Username already exists"}), 400

    is_valid, error_msg = _validate_password(password)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    hashed_password = generate_password_hash(password)
    user = {
        "id": len(USERS) + 1,
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "role": "user",
        "active": True,
        "name": name
    }
    USERS[username] = user
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/logout", methods=["POST"])
@require_token
def logout():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    REVOKED_ACCESS.add(token)
    body = request.get_json() or {}
    refresh_token = body.get("refresh_token")
    if refresh_token:
        try:
            decoded = jwt.decode(refresh_token, app.config['JWT_REFRESH_SECRET'], algorithms=['HS256'])
            tid = decoded.get('tid')
            if tid and tid in REFRESH_STORE:
                del REFRESH_STORE[tid]
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            pass
    return jsonify({"message": "Logged out successfully"})
@app.route("/test")
def test():
    user = {
        "id": 1,
        "username": "admin",
        "role": "admin"
    }
    return jsonify({        
        "access": create_access_token(user),
        "refresh": create_refresh_token(user),
        "test_decode_access": decode_access_token(create_access_token(user)),
        "test_decode_refresh": decode_refresh_token(create_refresh_token(user)),
        "store": REFRESH_STORE
    })

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    user = USERS.get(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Invalid username or password"}), 401
    if not user['active']:
        return jsonify({"error": "User account is inactive"}), 403
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    return jsonify({
        "access": access_token,
        "refresh": refresh_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_MIN * 60
    }), 200
    
    
@app.route('/me')
@require_token
def me():
    u = request.user 
    return jsonify({
        "id": u['id'],
        "username": u['username'],
        "email": u['email'],
        "role": u['role'],
        "name": u['name']
    })

@app.route("/admin")
@require_admin
def admin():
    return jsonify({"message": "you are admin"})

@app.route("/profile")
@require_scopes("read:profile")
def profile():
    return jsonify({"message": "You can read profile"})

@app.route("/users")
@require_scopes("read:users")
def list_users():
    return jsonify({"users": list(USERS.keys())})

@app.route("/users/delete", methods=["POST"])
@require_scopes("delete:users")
def delete_user():
    return jsonify({"message": "User deleted"})

if __name__ == "__main__":
    app.run(debug=True, port =8004)