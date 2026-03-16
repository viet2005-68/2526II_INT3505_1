from flask import Flask, jsonify, request

app = Flask(__name__)

# Dữ liệu giả định
books_db = {
    "book-1": {"type": "book", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "978-0743273565"},
    "book-2": {"type": "book", "title": "1984", "author": "George Orwell", "isbn": "978-0451524935"},
}

magazines_db = {
    "mag-1": {"type": "magazine", "title": "National Geographic", "issue": "Jan 2023", "publisher": "NatGeo"},
    "mag-2": {"type": "magazine", "title": "Time Magazine", "issue": "Feb 2023", "publisher": "Time Inc."},
}

# API Endpoints v1 (Chỉ có sách)
# Các ứng dụng cũ cứ vẫn gọi API này bình thường
@app.route('/api/v1/books', methods=['GET'])
def get_books_v1():
    # Giả sử chúng ta chỉ muốn trả về dữ liệu sách
    return jsonify({"data": [b for b in books_db.values() if b['type'] == 'book']})

@app.route('/api/v1/books/<string:book_id>', methods=['GET'])
def get_book_v1(book_id):
    book = books_db.get(book_id)
    if book and book['type'] == 'book': # Đảm bảo chỉ trả về sách
        return jsonify({"data": book})
    return jsonify({"error": "Book not found"}), 404

# --- API Endpoints V2 (Mở rộng cho nhiều loại tài liệu) ---
# Sử dụng một resource chung hơn: /library-items

# localhost:3000/api/v2/library-items?type=magazine
@app.route('/api/v2/library-items', methods=['GET'])
def get_library_items_v2():
    item_type = request.args.get('type')
    all_items = []
    if item_type:
        if item_type == 'book':
            all_items.extend(books_db.values())
        elif item_type == 'magazine':
            all_items.extend(magazines_db.values())
         # Mở rộng với nhiều loại tài liệu khác nhau như dvd hay đĩa cd, băng cassette, ...,
        else:
            return jsonify({"error": "Invalid type"}), 400
        
    else:
        all_items.extend(books_db.values())
        all_items.extend(magazines_db.values())
         # Mở rộng với nhiều loại tài liệu khác nhau như dvd hay đĩa cd, băng cassette, ...,

    # Ví dụ forward compatibility: thêm field mới mà client cũ vẫn bỏ qua được
    decorated_items = []
    for item in all_items:
        decorated = dict(item)
        decorated["thumbnailUrl"] = f"https://example.com/thumbnails/{decorated.get('title', 'item').replace(' ', '-').lower()}.jpg"
        decorated_items.append(decorated)

    return jsonify({"data": decorated_items}) 


@app.route('/api/v2/library-items/<string:item_id>', methods=['GET'])
def get_library_item_v2(item_id):
    item = books_db.get(item_id) or magazines_db.get(item_id) # Tìm cả trong sách và tạp chí
    if item:
        return jsonify({"data": item})
    return jsonify({"error": "Library item not found"}), 404

@app.route('/api/v2/library-items', methods=['POST'])
def add_library_item_v2():
    new_item = request.json
    item_type = new_item.get('type')

    if not item_type:
        return jsonify({"error": "Missing 'type' field"}), 400

    new_id = f"{item_type}-{len(books_db) + len(magazines_db) + 1}" # Tạo ID động

    if item_type == 'book':
        books_db[new_id] = new_item
    elif item_type == 'magazine':
        magazines_db[new_id] = new_item
    else:
        return jsonify({"error": f"Unsupported item type: {item_type}"}), 400

    return jsonify({"message": f"{item_type.capitalize()} added", "data": new_item}), 201


if __name__ == '__main__':
    app.run(debug=True, port=3000) 