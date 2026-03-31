from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import jwt
import secrets

app = Flask(__name__)
app.config["JWT_ACCESS_SECRET"] = os.getenv("JWT_ACCESS_SECRET", "dev-access-secret-key-change-in-production")
app.config["JWT_REFRESH_SECRET"] = os.getenv("JWT_REFRESH_SECRET", "dev-refresh-secret-key-change-in-production")
ACCESS_MIN = int(os.getenv('ACCESS_MIN', '15'))
REFRESH_DAYS = int(os.getenv('REFRESH_DAYS', '7'))

USERS = {}
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
    payload = {
        'sub': user['id'],
        'usr': user['username'],
        'role': user['role'],
        'type': 'access',
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=ACCESS_MIN)).timestamp()),
    }
    return jwt.encode(payload, app.config['JWT_ACCESS_SECRET'], algorithm='HS256')


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
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    data = decode_refresh_token(token)
    if not data:
        return jsonify({"error": "Invalid refresh token"}), 401
    user = {
        "id": data['sub'],
        "username": data['usr'],
        "role": "ADMIN"
    }
    
    new_access = create_access_token(user)
    return jsonify({"access": new_access})

@app.route("/logout", methods=["POST"])
def logout():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    data = decode_access_token(token)
    if not data:
        return jsonify({"error": "Invalid access token"}), 401
    REVOKED_ACCESS.add(token)
    return jsonify({"message": "Logged out successfully"})
   
@app.route("/test")
def test():
    user = {
        "id": 1,
        "username": "admin",
        "role": "ADMIN"
    }
    return jsonify({        
        "access": create_access_token(user),
        "refresh": create_refresh_token(user),
        "test_decode_access": decode_access_token(create_access_token(user)),
        "test_decode_refresh": decode_refresh_token(create_refresh_token(user)),
        "store": REFRESH_STORE
    })

if __name__ == "__main__":
    app.run(debug=True, port =8003)