from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
port = 4010

# Secret key để ký JWT – trong thực tế nên lưu ở biến môi trường
JWT_SECRET = "super-secret-key-for-demo"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 30

MOCK_USERS = [
    {"username": "alice", "password": "123456"},
    {"username": "bob",   "password": "abcdef"},
]

def generate_token(username):
    """Tạo JWT token với thời hạn 30 phút."""
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
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Nhập token theo dạng: Bearer <token>",
        }
    },
}
swagger = Swagger(app, template_file="openapi.yaml")

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
    # Offset-based pagination
    # Example: GET /books?offset=0&limit=10
    offset = request.args.get("offset", default=0, type=int)
    limit = request.args.get("limit", default=10, type=int)

    if offset < 0:
        offset = 0
    if limit <= 0:
        limit = 10

    paginated_books = books[offset: offset + limit]
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