from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
port = 4003

user_data = [{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "createdAt": datetime.now().isoformat()
}]



# 1. Tên Endpoint dùng danh từ (resource)
# RÕ RÀNG: 'POST' lên 'users' nghĩa là tạo user mới
@app.route('/users', methods=['POST'])
def create_user():
    body = request.get_json() or {}
    # Thông báo lỗi cần rõ ràng và cụ thể
    if not body.get('email'):
        # RÕ RÀNG: Client biết ngay lỗi ở trường 'email' và lý do là 'required and ...'.
        return jsonify({
            "error": {
                "field": "email",
                "message": "Email is required"
            }
        }), 400

    new_id = max((u["id"] for u in user_data), default=0) + 1
    new_user = {
        "id": new_id,
        "name": body.get('name', 'Unknown'),
        "email": body.get('email'),
        "createdAt": datetime.now().isoformat()
    }
    user_data.append(new_user)

    # 2. Tên trường trong response tự mô tả
    # RÕ RÀNG: 'name' và 'createdAt' rất dễ hiểu.
    return jsonify(new_user), 201

@app.route('/articles', methods=['GET'])
def get_articles():
    # RÕ RÀNG: dùng tên tham số dễ hiểu
    status = request.args.get('status')                # 'status' thay vì 's'
    page = request.args.get('page', default=1, type=int) # 'page' thay vì 'p'
    page_size = request.args.get('pageSize', default=10, type=int) # 'pageSize' thay vì 'ps'

    articles = [
        {"id": 1, "title": "Article 1"},
        {"id": 2, "title": "Article 2"},
    ]

    return jsonify({
        "filters": {
            "status": status,
            "page": page,
            "pageSize": page_size
        },
        "data": articles
    }), 200

if __name__ == '__main__':
    app.run(port=4003)