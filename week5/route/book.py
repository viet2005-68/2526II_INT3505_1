from flask import Blueprint, jsonify
from database import db
from models import Book

books_bp = Blueprint("books", __name__, url_prefix="/books")


@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({
        "id": book.id,
        "title": book.title,
        "price": book.price,
        "author_id": book.author_id,
        "created_at": book.created_at.isoformat() if book.created_at else None,
    })
