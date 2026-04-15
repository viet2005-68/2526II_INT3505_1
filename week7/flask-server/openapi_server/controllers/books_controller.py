import math
import re
from typing import List, Tuple

import connexion
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from openapi_server import mongo
from openapi_server.models.book import Book
from openapi_server.models.create_book_payload import CreateBookPayload
from openapi_server.models.error import Error
from openapi_server.models.paginated_books_response import PaginatedBooksResponse
from openapi_server.models.pagination_metadata import PaginationMetadata


def _err(message: str, code: int) -> Tuple[Error, int]:
    return Error(error=message), code


def _doc_to_book(doc) -> Book:
    return Book(
        id=doc["_id"],
        title=doc["title"],
        author=doc["author"],
        year=doc["year"],
    )


def _search_filter(search: str) -> dict:
    s = (search or "").strip()
    if not s:
        return {}
    escaped = re.escape(s)
    return {
        "$or": [
            {"title": {"$regex": escaped, "$options": "i"}},
            {"author": {"$regex": escaped, "$options": "i"}},
        ]
    }


def api_books_book_id_delete(book_id):
    try:
        bid = int(book_id)
    except (ValueError, TypeError):
        return _err("Invalid book id", 400)
    try:
        doc = mongo.books_coll().find_one_and_delete({"_id": bid})
    except PyMongoError:
        return _err("Database error", 500)
    if not doc:
        return _err("Book not found", 404)
    return _doc_to_book(doc), 200


def api_books_book_id_get(book_id):
    try:
        bid = int(book_id)
    except (ValueError, TypeError):
        return _err("Invalid book id", 400)
    try:
        doc = mongo.books_coll().find_one({"_id": bid})
    except PyMongoError:
        return _err("Database error", 500)
    if not doc:
        return _err("Book not found", 404)
    return _doc_to_book(doc), 200


def api_books_book_id_put(book_id, body):
    try:
        bid = int(book_id)
    except (ValueError, TypeError):
        return _err("Invalid book id", 400)

    raw = connexion.request.get_json() if connexion.request.is_json else {}
    if not isinstance(raw, dict):
        raw = {}
    allowed = ("title", "author", "year")
    updates = {k: raw[k] for k in allowed if k in raw}
    if not updates:
        return _err("No fields to update", 400)

    set_doc = {}
    if "title" in updates:
        set_doc["title"] = updates["title"]
    if "author" in updates:
        set_doc["author"] = updates["author"]
    if "year" in updates:
        try:
            set_doc["year"] = int(updates["year"])
        except (ValueError, TypeError):
            return _err("year must be an integer", 400)

    try:
        doc = mongo.books_coll().find_one_and_update(
            {"_id": bid},
            {"$set": set_doc},
            return_document=ReturnDocument.AFTER,
        )
    except PyMongoError:
        return _err("Database error", 500)
    if not doc:
        return _err("Book not found", 404)
    return _doc_to_book(doc), 200


def api_books_get(page=None, limit=None, search=None):
    page = int(page) if page is not None else 1
    limit = int(limit) if limit is not None else 10
    if page < 1:
        return _err("page must be >= 1", 400)
    if limit < 1:
        return _err("limit must be >= 1", 400)

    filt = _search_filter(search or "")
    try:
        coll = mongo.books_coll()
        total = coll.count_documents(filt)
        cursor = coll.find(filt).sort("_id", 1).skip((page - 1) * limit).limit(limit)
        items: List[Book] = [_doc_to_book(d) for d in cursor]
    except PyMongoError:
        return _err("Database error", 500)

    total_pages = math.ceil(total / limit) if limit else 0
    meta = PaginationMetadata(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
    )
    return PaginatedBooksResponse(data=items, metadata=meta), 200


def api_books_post(body):
    create_book_payload = body
    if connexion.request.is_json:
        create_book_payload = CreateBookPayload.from_dict(connexion.request.get_json())

    if (
        create_book_payload.title is None
        or create_book_payload.author is None
        or create_book_payload.year is None
    ):
        return _err("title, author, and year are required", 400)

    try:
        bid = mongo.next_book_id()
        doc = {
            "_id": bid,
            "title": create_book_payload.title,
            "author": create_book_payload.author,
            "year": int(create_book_payload.year),
        }
        mongo.books_coll().insert_one(doc)
    except PyMongoError:
        return _err("Database error", 500)
    except (ValueError, TypeError):
        return _err("year must be an integer", 400)

    return _doc_to_book(doc), 201
