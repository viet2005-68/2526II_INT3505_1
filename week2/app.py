import re
from flask import Flask, request, jsonify
import uuid
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-change-in-demo-INT3505"
app.config["JWT_EXPIRE_HOURS"] = 24
app.config["PASSWORD_MIN_LENGTH"] = 6
app.config["USERNAME_MIN_LENGTH"] = 3
app.config["USERNAME_MAX_LENGTH"] = 32


_now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
USERS = {
    "admin": {"password": "admin", "email": None, "created_at": _now},
    "user": {"password": "user123", "email": None, "created_at": _now},
}

books = [
    {"id": 1, "title": "Book 1"},
    {"id": 2, "title": "Book 2"}
]

@app.route("/books", methods=["GET"])
def get_books():
    return jsonify(books)


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """Uniform Interface: resource được định danh bằng URI /books/<id>."""
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)


@app.route("/books-cacheable", methods=["GET"])
def get_books_cacheable():
    """
    Demo Cacheable: Response có Cache-Control header.
    Client/Browser có thể cache 60 giây, giảm request tới server.
    """
    response = jsonify(books)
    response.headers["Cache-Control"] = "public, max-age=60"
    response.headers["X-Cache-Info"] = "Cacheable for 60 seconds"
    return response


@app.route("/demo-stateless", methods=["GET"])
def demo_stateless():

    request_id = str(uuid.uuid4())[:8]
    return jsonify({
        "message": "Stateless: Mỗi request độc lập",
        "request_id": request_id,
        "note": "Request_id khác nhau mỗi lần = Server không lưu state"
    })


def create_token(username):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "exp": now + timedelta(hours=app.config["JWT_EXPIRE_HOURS"]),
        "iat": now,
    }
    return jwt.encode(
        payload, app.config["SECRET_KEY"], algorithm="HS256"
    )


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth.split(" ")[1]
        try:
            payload = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            request.current_user = payload.get("sub")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


def _user_response(username: str):
    u = USERS.get(username)
    if not u:
        return None
    return {
        "username": username,
        "email": u.get("email"),
        "created_at": u.get("created_at"),
    }


@app.route("/auth/register", methods=["POST"])
def register():
    """
    Đăng ký tài khoản mới.
    Body: {"username": "...", "password": "...", "email": "..." (optional)}
    Trả về user + access_token (đăng nhập luôn sau khi đăng ký).
    """
    data = request.get_json() or {}
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "")
    email = (str(data.get("email") or "").strip() or None) or None

    # Validation
    if not username:
        return jsonify({"error": "username is required"}), 400
    if len(username) < app.config["USERNAME_MIN_LENGTH"]:
        return jsonify({
            "error": f"username must be at least {app.config['USERNAME_MIN_LENGTH']} characters"
        }), 400
    if len(username) > app.config["USERNAME_MAX_LENGTH"]:
        return jsonify({
            "error": f"username must be at most {app.config['USERNAME_MAX_LENGTH']} characters"
        }), 400
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return jsonify({
            "error": "username may only contain letters, numbers and underscore"
        }), 400
    if username.lower() in (u.lower() for u in USERS):
        return jsonify({"error": "username already taken"}), 409
    if not password:
        return jsonify({"error": "password is required"}), 400
    if len(password) < app.config["PASSWORD_MIN_LENGTH"]:
        return jsonify({
            "error": f"password must be at least {app.config['PASSWORD_MIN_LENGTH']} characters"
        }), 400
    if email and not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return jsonify({"error": "invalid email format"}), 400

    # Tạo user (lưu plain password, chỉ dùng demo)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    USERS[username] = {
        "password": password,
        "email": email,
        "created_at": now,
    }
    user_info = {"username": username, "email": email, "created_at": now}
    token = create_token(username)
    return jsonify({
        "message": "Registration successful",
        "user": user_info,
        "access_token": token,
        "token_type": "bearer",
        "expires_in_hours": app.config["JWT_EXPIRE_HOURS"],
    }), 201


@app.route("/auth/login", methods=["POST"])
def login():
    """Đăng nhập, trả về JWT. Body: {"username": "...", "password": "..."}"""
    data = request.get_json() or {}
    username = data.get("username")
    password = str(data.get("password"))
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    u = USERS.get(username)
    if not u or u["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_token(username)
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "expires_in_hours": app.config["JWT_EXPIRE_HOURS"],
        "user": _user_response(username),
    }), 200


@app.route("/books", methods=["POST"])
@jwt_required
def add_book():
    data = request.get_json() or {}
    new_id = max((b["id"] for b in books), default=0) + 1
    new_book = {"id": new_id, "title": data.get("title", "Untitled")}
    books.append(new_book)
    return jsonify({"message": "Book added", "data": new_book}), 201

@app.route("/books/<int:book_id>", methods=["PUT"])
@jwt_required
def update_book(book_id):
    data = request.get_json() or {}
    for book in books:
        if book["id"] == book_id:
            book.update(data)
            return jsonify({"message": "Book updated"}), 200
    return jsonify({"error": "Book not found"}), 404

@app.route("/books/<int:book_id>", methods=["DELETE"])
@jwt_required
def delete_book(book_id):
    for i, book in enumerate(books):
        if book["id"] == book_id:
            books.pop(i)
            return jsonify({"message": "Book deleted"}), 200
    return jsonify({"error": "Book not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
