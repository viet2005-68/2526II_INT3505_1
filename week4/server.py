from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__) 
port = 4010


app.config["SWAGGER"] = {
    "title": "Book API",
    "uiversion": 3,
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
def update_book(book_id):
    data = request.get_json()
    for book in books:
        if book["id"] == book_id:
            book.update(data)
            return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

@app.route("/books/<int:book_id>", methods=["DELETE"])
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