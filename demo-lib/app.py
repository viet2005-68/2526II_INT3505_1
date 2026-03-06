from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# Stateless: KHÔNG lưu session/state giữa các request
# Mỗi request độc lập, server không "nhớ" request trước

books = [
    {"id": 1, "title": "Book 1"},
    {"id": 2, "title": "Book 2"}
]

@app.route("/books", methods=["GET"])
def get_books():
    return jsonify(books)


@app.route("/demo-stateless", methods=["GET"])
def demo_stateless():
    """
    Demo Stateless: Mỗi request trả về request_id MỚI.
    Server KHÔNG lưu state - không session, không cookie.
    Request sau không "biết" gì về request trước.
    """
    request_id = str(uuid.uuid4())[:8]
    return jsonify({
        "message": "Stateless: Mỗi request độc lập",
        "request_id": request_id,
        "note": "Request_id khác nhau mỗi lần = Server không lưu state"
    })

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
