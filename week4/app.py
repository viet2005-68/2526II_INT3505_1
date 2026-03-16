from flask import Flask, request, jsonify

app = Flask(__name__) 
port = 4004

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

@app.route("/books", methods=["GET"])
def get_books():
    return jsonify(books)

@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json()
    new_id = max((b["id"] for b in books), default=0) + 1
    new_book = {
        "id": new_id,
        "title": data["title"],
        "author": data["author"],
        "year": data["year"]
    }
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