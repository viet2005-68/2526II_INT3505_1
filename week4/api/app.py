from flask import Flask, request, jsonify, send_from_directory
from flasgger import Swagger
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from functools import wraps
import jwt
import datetime
import os

app = Flask(__name__)
port = 4001

JWT_SECRET = "super-secret-key-for-demo"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 30

BASE_DIR = os.path.dirname(__file__)

MOCK_USERS = [
    {"username": "alice", "password": "123456"},
    {"username": "bob",   "password": "abcdef"},
]

def generate_token(username):
    payload = {
        "sub": username,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def require_token(f):
    """Decorator kiểm tra Bearer JWT token từ header Authorization."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing Bearer token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


app.config["SWAGGER"] = {
    "title": "Book API",
    "uiversion": 3,
}
swagger = Swagger(app, template_file=os.path.join(BASE_DIR, "openapi.yaml"))

# Serve openapi.yaml – hoạt động cả local lẫn Vercel
@app.route("/openapi.yaml")
def serve_openapi():
    return send_from_directory(BASE_DIR, "openapi.yaml")

# Swagger UI cùng domain -> cookie hoạt động
SWAGGER_UI_BLUEPRINT = get_swaggerui_blueprint(
    "/docs",
    "/openapi.yaml",
    config={"app_name": "Book API"}
)
app.register_blueprint(SWAGGER_UI_BLUEPRINT, url_prefix="/docs")

books = [
    {
        "id": 1,
        "title": "Book 1",
        "author": "Author 1",
        "year": 2020
    },
    {
        "id": 2,
        "title": "Book 2",
        "author": "Author 2",
        "year": 2021
    }
]

CORS(app)

@app.route("/set-cookie")
def set_cookie():
    """
    Helper endpoint để set cookie debug và theme trên trình duyệt.
    Truy cập: http://localhost:4001/set-cookie?debug=1&theme=dark
    Sau đó vào /docs để Swagger UI tự gửi cookie.
    """
    debug = request.args.get("debug", "0")
    theme = request.args.get("theme", "light")
    resp = jsonify({
        "message": "Cookie set! Now go to /docs and try GET /books",
        "cookies": {"debug": debug, "theme": theme}
    })
    resp.set_cookie("debug", debug)
    resp.set_cookie("theme", theme)
    return resp


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = next((u for u in MOCK_USERS if u["username"] == username and u["password"] == password), None)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    token = generate_token(username)
    return jsonify({"token": token}), 200


@app.route("/books", methods=["GET"])
def get_books():
    offset = request.args.get("offset", default=0, type=int)
    limit = request.args.get("limit", default=10, type=int)

    if offset < 0:
        offset = 0
    if limit <= 0:
        limit = 10

    paginated_books = books[offset: offset + limit]

    # Đọc debug từ cookie (gửi qua header Cookie: debug=1; theme=dark)
    debug = request.cookies.get("debug", "0")
    if debug == "1":
        return jsonify({
            "data": paginated_books,
            "debug": {
                "offset": offset,
                "limit": limit,
                "returned": len(paginated_books),
                "total": len(books),
            }
        })

    return jsonify(paginated_books)

@app.route("/books", methods=["POST"])
@require_token
def create_book():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    title = data.get("title")
    author = data.get("author")
    year = data.get("year")

    if not title or not author or not year:
        return jsonify({"error": "Title, author and year are required"}), 400
    if not isinstance(year, int):
        return jsonify({"error": "Year must be an integer"}), 400
    if not isinstance(title, str):
        return jsonify({"error": "Title must be a string"}), 400
    if not isinstance(author, str):
        return jsonify({"error": "Author must be a string"}), 400

    new_id = max((b["id"] for b in books), default=0) + 1
    new_book = {"id": new_id, "title": title, "author": author, "year": year}
    books.append(new_book)
    return jsonify(new_book), 201

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

@app.route("/books/<int:book_id>", methods=["PUT"])
@require_token
def update_book(book_id):
    data = request.get_json()
    for book in books:
        if book["id"] == book_id:
            book.update(data)
            return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

@app.route("/books/<int:book_id>", methods=["DELETE"])
@require_token
def delete_book(book_id):
    for i, book in enumerate(books):
        if book["id"] == book_id:
            books.pop(i)
            return jsonify({"message": "Book deleted"}), 200
    return jsonify({"error": "Book not found"}), 404

@app.route("/")
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True, port=port)