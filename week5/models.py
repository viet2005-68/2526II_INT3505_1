from datetime import datetime
from database import db


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(BaseModel):
    __tablename__ = 'users'
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    loans = db.relationship('Loan', back_populates='user', cascade='all, delete-orphan')


class Author(BaseModel):
    __tablename__ = 'authors'
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', back_populates='author', cascade='all, delete-orphan')


class Book(BaseModel):
    __tablename__ = 'books'
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    author = db.relationship('Author', back_populates='books')
    loans = db.relationship('Loan', back_populates='book', cascade='all, delete-orphan')
    quantity = db.Column(db.Integer, nullable=False, default=1)


class Loan(BaseModel):
    __tablename__ = 'loans'
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    book = db.relationship('Book', back_populates='loans')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='loans')
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
