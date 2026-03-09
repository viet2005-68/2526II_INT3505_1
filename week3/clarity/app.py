from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 1. Tên Endpoint dùng danh từ (resource)
# RÕ RÀNG: 'POST' lên 'users' nghĩa là tạo user mới
@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    # Thông báo lỗi cần rõ ràng và cụ thể
    if not user_data.get('email'):
        # RÕ RÀNG: Client biết ngay lỗi ở trường 'email' và lý do là 'required and ...'.
        return jsonify({
            "error": {
                "field": "email",
                "message": "Email is required"
            }
        }), 400
    
    # 2. Tên trường trong response tự mô tả
    # RÕ RÀNG: 'name' và 'createdAt' rất dễ hiểu.
    return jsonify({
        "id": 1,
        "name": user_data.get('name', 'Unknown'),
        "email": user_data.get('email'),
        "createdAt": datetime.now().isoformat()
    }), 201

@app.route('/articles', methods=['GET'])
def get_articles():
    status = request.args.get('status') # 'status' thay vì 's'
    page = request.args.get('page', 1, type=int) # 'page' thay vì 'p'

    return jsonify({
        "filters": {
            "status": status,
            "page": page
        },
        "data": [{"id": 1, "title": "Article 1"}] # Dùng 'data' cho nhất quán
    }), 200

if __name__ == '__main__':
    app.run(port=4003)