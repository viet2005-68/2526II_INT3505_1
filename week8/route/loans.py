from flask import Blueprint, request
from database import db
from models import Loan, User, Book
from utils.response import api_response, api_error

loans_bp = Blueprint("loans", __name__, url_prefix="/")


# Get all loans of a user
@loans_bp.route("/users/<int:user_id>/loans", methods=["GET"])
def get_loans_by_user(user_id):
    """Lấy tất cả loan của một user"""
    user = db.session.get(User, user_id)
    if not user:
        return api_error("User not found", status_code=404)
    
    loans = db.session.query(Loan).filter_by(user_id=user_id).all()
    data = []
    for loan in loans:
        data.append({
            "id": loan.id,
            "user_id": loan.user_id,
            "book": {
                "id": loan.book.id,
                "title": loan.book.title,
                "price": loan.book.price,
                "author": {
                    "id": loan.book.author.id,
                    "name": loan.book.author.name
                }
            },
            "loan_date": loan.loan_date.isoformat() if loan.loan_date else None,
            "return_date": loan.return_date.isoformat() if loan.return_date else None,
            "status": "returned" if loan.return_date else "active"
        })
    
    return api_response(data=data, metadata={"resource": "loans", "count": len(data)})


# Loan a book to a user
@loans_bp.route("/users/<int:user_id>/loans", methods=["POST"])
def loan_book(user_id):
    try:
        data = request.get_json()
        if not data:
            return api_error("Request body is required", status_code=400)
    except Exception:
        return api_error("Invalid JSON format", status_code=400)
    
    book_id = data.get("book_id")
    
    if not book_id:
        return api_error("book_id is required", status_code=400)
    
    user = db.session.get(User, user_id)
    book = db.session.get(Book, book_id)

    if not user:
        return api_error("User not found", status_code=404)
    if not book:
        return api_error("Book not found", status_code=404)

    if book.quantity < 1:
        return api_error("Book is not available", status_code=400)

    existing_loan = db.session.query(Loan).filter_by(
        user_id=user_id, 
        book_id=book_id
    ).filter(Loan.return_date.is_(None)).first()
    
    if existing_loan:
        return api_error("User already has this book on loan", status_code=400)

    loan = Loan(user_id=user_id, book_id=book_id)
    book.quantity -= 1

    db.session.add(loan)
    db.session.commit()

    return api_response(
        data={
            "id": loan.id,
            "user_id": loan.user_id,
            "book": {
                "id": loan.book.id,
                "title": loan.book.title,
                "price": loan.book.price,
                "author": {
                    "id": loan.book.author.id,
                    "name": loan.book.author.name
                }
            },
            "loan_date": loan.loan_date.isoformat() if loan.loan_date else None,
            "return_date": loan.return_date.isoformat() if loan.return_date else None,
            "status": "returned" if loan.return_date else "active"
        },
        metadata={"resource": "loan"},
        status_code=201
    )


# Return a book
@loans_bp.route("/users/<int:user_id>/loans/<int:loan_id>/return", methods=["POST"])
def return_book(user_id, loan_id):

    try:
        data = request.get_json() or {}
    except Exception:
        return api_error("Invalid JSON format", status_code=400)
    

    user = db.session.get(User, user_id)
    if not user:
        return api_error("User not found", status_code=404)
    
    loan = db.session.get(Loan, loan_id)
    if not loan:
        return api_error("Loan not found", status_code=404)
   
    if loan.user_id != user_id:
        return api_error("Unauthorized: Loan does not belong to this user", status_code=403)
    

    if loan.return_date:
        return api_error("Book has already been returned", status_code=400)

    # Cập nhật return_date
    loan.return_date = db.func.now()
    book = db.session.get(Book, loan.book_id)
    book.quantity += 1

    db.session.commit()

    return api_response(
        data={
            "id": loan.id,
            "user_id": loan.user_id,
            "book": {
                "id": loan.book.id,
                "title": loan.book.title,
                "price": loan.book.price,
                "author": {
                    "id": loan.book.author.id,
                    "name": loan.book.author.name
                }
            },
            "loan_date": loan.loan_date.isoformat() if loan.loan_date else None,
            "return_date": loan.return_date.isoformat() if loan.return_date else None,
            "status": "returned" if loan.return_date else "active"
        },
        metadata={"resource": "loan_returned"},
        status_code=200
    )