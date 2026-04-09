"""
W6: OFFSET vs CURSOR pagination demo — books in SQLite.
Run: python app.py
OpenAPI: http://127.0.0.1:8080/openapi.yaml  |  Swagger UI: http://127.0.0.1:8080/docs
"""

import os
import sqlite3
import time

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CORS(app)

app.register_blueprint(
    get_swaggerui_blueprint(
        "/docs",
        "/openapi.yaml",
        config={"app_name": "Homework W6 — Books API"},
    ),
    url_prefix="/docs",
)


@app.route("/openapi.yaml")
def serve_openapi():
    return send_from_directory(BASE_DIR, "openapi.yaml")

DB = "books.db"
N = 1000000


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS books")
    cur.execute(
        """
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            year INTEGER
        )
        """
    )
    print("Seeding...")
    row = ("Test Book", "Test Author", 2006)
    data = [row] * N
    cur.executemany(
        "INSERT INTO books (title, author, year) VALUES (?, ?, ?)", data
    )
    conn.commit()
    conn.close()
    print("Done.")


@app.route("/api/v1/books", methods=["GET"])
def get_books():
    start = time.time()
    pagination_type = request.args.get("pagination", "offset")
    limit = int(request.args.get("limit", 10))

    conn = get_db()
    cur = conn.cursor()

    if pagination_type == "offset":
        offset = int(request.args.get("offset", 0))
        cur.execute(
            "SELECT * FROM books ORDER BY id LIMIT ? OFFSET ?", (limit, offset)
        )
        rows = cur.fetchall()
        conn.close()
        return jsonify(
            {
                "type": "offset",
                "limit": limit,
                "offset": offset,
                "time": time.time() - start,
                "data": [dict(r) for r in rows],
            }
        )

    if pagination_type == "cursor":
        last_id = request.args.get("last_id")
        if last_id:
            cur.execute(
                "SELECT * FROM books WHERE id > ? ORDER BY id LIMIT ?",
                (int(last_id), limit),
            )
        else:
            cur.execute("SELECT * FROM books ORDER BY id LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        next_cursor = rows[-1]["id"] if rows else None
        return jsonify(
            {
                "type": "cursor",
                "limit": limit,
                "next_cursor": next_cursor,
                "time": time.time() - start,
                "data": [dict(r) for r in rows],
            }
        )

    conn.close()
    return jsonify({"error": "pagination must be offset or cursor"}), 400


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Book API — OFFSET vs CURSOR",
            "openapi_spec": "/openapi.yaml",
            "swagger_ui": "/docs/",
            "offset_example": "/api/v1/books?limit=10&offset=90000&pagination=offset",
            "cursor_example": "/api/v1/books?limit=10&last_id=90000&pagination=cursor",
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8080)
