from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
port = 4001

books = [
    {"id": 1, "title": "Doraemon", "author": "Fujiko Fujio", "year": 1969},
    {"id": 2, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925},
]

CORS(app)

@app.route("/books", methods=["GET"])
def get_books():
    return jsonify(books)

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)

if __name__ == "__main__":
    app.run(debug=True, port=port)
