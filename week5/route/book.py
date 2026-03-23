from flask import Blueprint, request
from database import db
from models import Book, Author
from utils.response import api_response, api_error

books_bp = Blueprint("books", __name__, url_prefix="/books")


@books_bp.route("/", methods=["GET"])
def list_books():
    
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    
    books = db.session.query(Book).options(db.joinedload(Book.author)).offset((page - 1) * per_page).limit(per_page).all()
    data = []
    for book in books:
        data.append({
            "id": book.id,
            "title": book.title,
            "price": book.price,
            "author": {
                "id": book.author.id,
                "name": book.author.name
            },
            "created_at": book.created_at.isoformat() if book.created_at else None,
        })
    return api_response(data=data, metadata={"resource": "books", "count": len(data), "page": page, "per_page": per_page})

@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return api_error("Book not found", status_code=404)
    data = {
        "id": book.id,
        "title": book.title,
        "price": book.price,
        "author_id": book.author_id,
        "created_at": book.created_at.isoformat() if book.created_at else None,
    }
    return api_response(data=data, metadata={"resource": "book"})

@books_bp.route("/", methods=["POST"])
def create_book():
    data = request.get_json()
    author_name = data.get("author_name")
    
    if not author_name:
        return api_error("Author name is required", status_code=400)
    if not data.get("title") or not data.get("price"):
        return api_error("Title and price are required", status_code=400)

    author = db.session.query(Author).filter_by(name=author_name).first()
    if not author:
        author = Author(name=author_name)
        db.session.add(author)
        db.session.flush()
        
    book = Book(
        title=data.get("title"),
        price=data.get("price"),
        author_id=author.id,
        quantity=data.get("quantity", 1)
    )
    author = db.session.get(Author, book.author_id)
    db.session.add(book)
    db.session.commit()
    return api_response(data={"id": book.id}, metadata={"resource": "book"}, status_code=201)

@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return api_error("Book not found", status_code=404)
    db.session.delete(book)
    db.session.commit()
    return api_response(data=None, metadata={"resource": "book"}, status_code=204)  

@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return api_error("Book not found", status_code=404)

    data = request.get_json()
    if "title" in data:
        book.title = data["title"]
    if "price" in data:
        book.price = data["price"]
    if "quantity" in data:
        book.quantity = data["quantity"]
    if "author_name" in data:
        author_name = data["author_name"]
        author = db.session.query(Author).filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.flush()
        book.author_id = author.id

    db.session.commit()
    return api_response(data=None, metadata={"resource": "book"}, status_code=200)