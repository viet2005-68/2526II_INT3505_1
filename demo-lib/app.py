from flask import Flask, request, jsonify

app = Flask(__name__)

books = [
    {"id": 1, "title": "Book 1"},
    {"id": 2, "title": "Book 2"}
]

@app.route("/books", methods=["GET"])
def get_books():
    return jsonify(books)

@app.route("/books", methods=["POST"])
def add_book():
    data = request.json
    books.append(data)
    return jsonify({"message": "Book added"}), 201

@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.json
    for book in books:
        if book["id"] == book_id:
            book.update(data)
            return jsonify({"message": "Book updated"}), 200
    return jsonify({"error": "Book not found"}), 404

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    for i, book in enumerate(books):
        if book["id"] == book_id:
            books.pop(i)
            return jsonify({"message": "Book deleted"}), 200
    return jsonify({"error": "Book not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
