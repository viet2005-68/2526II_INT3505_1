from flask import Flask, jsonify, request

app = Flask(__name__)
port = 3002

# Dữ liệu đã được chuẩn hóa key (id, name)

# - Các resource khác nhau nên dùng cùng naming convention
# - Không nên lúc thì product_id, lúc thì id
mock_users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

mock_products = [
    {"id": 101, "name": "Laptop"},
    {"id": 102, "name": "Mouse"}
]

mock_orders = [
    {"id": 1001, "userId": 1, "productId": 101, "quantity": 2, "status": "completed"},
    {"id": 1002, "userId": 2, "productId": 102, "quantity": 1, "status": "pending"},
    {"id": 1003, "userId": 1, "productId": 102, "quantity": 3, "status": "completed"}
]

# CONSISTENT RESPONSE STRUCTURE 
# CONSISTENT RESPONSE FORMAT
# Helper function này đảm bảo TẤT CẢ API trả về cùng một cấu trúc JSON.
#
# Consistency ở đây nghĩa là:
# - mọi endpoint đều trả về field "statnfo?id=1us"
# - dữ liệu luôn nằm trong "data"
# - metadata luôn nằm trong "pagination"
#
# Nhờ vậy frontend có thể xử lý response theo một cách duy nhất.


# Consistent Success Response
def create_api_success_response(data, page=None, limit=None, total=None):
    if total is not None:
        total_items = total
    elif isinstance(data, (list, tuple)):
        total_items = len(data)
    elif data is None:
        total_items = 0
    else:
        total_items = 1

    return {
        "status": "success",
        "data": data,
        "metadata": {
            "pagination": {
                "page": page,
                "limit": limit,
                "totalItems": total_items
            }
        }
    }



# Consistent Error Response
# Khi xảy ra lỗi, API cũng phải trả về format giống nhau.
#
# Ví dụ:
# {
#   "status": "error",
#   "message": "User not found"
# }
#
# Điều này giúp client dễ xử lý lỗi.
def create_api_error_response(message, status_code=400):
    return jsonify({
        "status": "error",
        "message": message
    }), status_code



# PRINCIPLE 1: Consistent API Structure
# RESTful endpoint nên dùng danh từ số nhiều.
# Nên dùng chữ thường, không dùng chữ hoa.
# Good:
# /users
# /products
#
# Bad:
# /getUsers
# /fetchProducts



@app.route('/users', methods=['GET'])
def get_users():
    print("Request /users")

    name = request.args.get("name")

    users = mock_users
    if name:
        users = [u for u in users if name.lower() in u["name"].lower()]

    return jsonify(create_api_success_response(users))


@app.route('/users', methods=['POST'])
def create_user():
    """
    PRINCIPLE: POST /users -> tạo mới user
    - Body JSON ví dụ: { "name": "Charlie" }
    - Server tạo id mới, trả về user vừa tạo
    """
    body = request.get_json() or {}
    name = body.get("name")

    if not name:
        return create_api_error_response("Field 'name' is required", 400)

    # Giả lập auto-increment ID
    new_id = max((u["id"] for u in mock_users), default=0) + 1
    new_user = {"id": new_id, "name": name}
    mock_users.append(new_user)

    return jsonify(create_api_success_response(new_user)), 201


# PRINCIPLE 3: Resource by ID
# CONSISTENT RESOURCE BY ID 
# Endpoint lấy resource theo ID luôn dùng pattern:
#
# /resource/{id}
#
# Ví dụ:
# /users/1
# /products/101

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = next((u for u in mock_users if u["id"] == user_id), None)

    if not user:
        return create_api_error_response("User not found", 404)

    # CONSISTENCY PRINCIPLE:
    # API này trả dữ liệu users nhưng vẫn sử dụng cùng một cấu trúc response
    # thông qua hàm create_api_success_response().
    return jsonify(create_api_success_response(user))


@app.route('/users/<int:user_id>', methods=['PUT'])
def replace_user(user_id):
    """
    PRINCIPLE: PUT /users/{id} -> cập nhật TOÀN BỘ user
    - Body phải chứa đầy đủ các field cần thiết, ví dụ:
      { "name": "New Name" }
    """
    body = request.get_json() or {}
    name = body.get("name")

    if not name:
        return create_api_error_response("Field 'name' is required", 400)

    user = next((u for u in mock_users if u["id"] == user_id), None)
    if not user:
        return create_api_error_response("User not found", 404)

    user["name"] = name

    return jsonify(create_api_success_response(user))


@app.route('/users/<int:user_id>', methods=['PATCH'])
def update_user_partial(user_id):
    """
    PRINCIPLE: PATCH /users/{id} -> cập nhật MỘT PHẦN user
    - Body có thể chỉ chứa 1 phần field, ví dụ:
      { "name": "Partial Updated Name" }
    """
    body = request.get_json() or {}

    user = next((u for u in mock_users if u["id"] == user_id), None)
    if not user:
        return create_api_error_response("User not found", 404)

    # Chỉ update những field có trong body
    if "name" in body:
        user["name"] = body["name"]

    return jsonify(create_api_success_response(user))


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    PRINCIPLE: DELETE /users/{id} -> xóa user
    """
    global mock_users

    user = next((u for u in mock_users if u["id"] == user_id), None)
    if not user:
        return create_api_error_response("User not found", 404)

    mock_users = [u for u in mock_users if u["id"] != user_id]

    # Trả về status success nhưng không cần data chi tiết
    return jsonify(create_api_success_response({"id": user_id}))


# PRINCIPLE: SUB-RESOURCES
# Ví dụ về cấu trúc phân cấp:
# /users/{id}/products -> danh sách sản phẩm liên quan tới 1 user
@app.route('/users/<int:user_id>/products', methods=['GET'])
def get_user_products(user_id):
    """
    Ví dụ sub-resource:
    - GET /users/{id}/products
    Ở đây để đơn giản ta giả sử:
    - user lẻ (1, 3, ...) -> sản phẩm có id lẻ
    - user chẵn (2, 4, ...) -> sản phẩm có id chẵn
    """
    user = next((u for u in mock_users if u["id"] == user_id), None)
    if not user:
        return create_api_error_response("User not found", 404)

    if user_id % 2 == 0:
        user_products = [p for p in mock_products if p["id"] % 2 == 0]
    else:
        user_products = [p for p in mock_products if p["id"] % 2 == 1]

    return jsonify(create_api_success_response(user_products))


# PRINCIPLE 4: Pagination

# CONSISTENT PAGINATION 
# Pagination parameters được dùng thống nhất:
#
# page  -> trang hiện tại
# limit -> số item mỗi trang
#
# Ví dụ:
# /products?page=1&limit=10
@app.route('/products', methods=['GET'])
def get_products():
    print("Request /products")

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 2))

    start = (page - 1) * limit
    end = start + limit

    paginated_products = mock_products[start:end]

    return jsonify(create_api_success_response(
        paginated_products,
        total=len(mock_products),
        page=page,
        limit=limit
    ))



# PRINCIPLE 5:
# Sử dụng method để định nghĩa hành động
# thay vì đưa hành động vào URL


# BAD PRACTICE – không nên làm
# Vừa nhét hành động vào URL, vừa trộn nhiều nghĩa cho cùng 1 endpoint

"""
@app.route('/products/create', methods=['POST'])
def create_order_bad():
    # ...
    pass

# /orders/delete/<id> dùng GET để xóa dữ liệu 
@app.route('/products/delete/<int:product_id>', methods=['GET'])
def delete_order_bad(order_id):
    # ...
    pass

# /orders/action/<id> trộn PATCH và DELETE trong cùng 1 handler
@app.route('/products/action/<int:product_id>', methods=['PATCH', 'DELETE'])
def manage_product_bad(product_id):
    if request.method == 'PATCH':
        # Vừa cập nhật một phần...
        pass
    elif request.method == 'DELETE':
        # ...vừa xóa luôn, chung 1 URL /orders/action
        pass"""

# GOOD: URL là tài nguyên (orders), mỗi HTTP method 1 ý nghĩa duy nhất
# TẠO mới product
@app.route('/products', methods=['POST'])
def create_product():
    body = request.get_json() or {}
    name = body.get("name")

    if not name:
        return create_api_error_response("Field 'name' is required", 400)

    # Giả lập auto-increment ID
    new_id = max((p["id"] for p in mock_products), default=100) + 1
    new_product = {"id": new_id, "name": name}
    mock_products.append(new_product)

    return jsonify(create_api_success_response(new_product)), 201

# LẤY chi tiết 1 product
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in mock_products if p["id"] == product_id), None)

    if not product:
        return create_api_error_response("Product not found", 404)

    return jsonify(create_api_success_response(product))

# CẬP NHẬT TOÀN BỘ product
@app.route('/products/<int:product_id>', methods=['PUT'])
def replace_product(product_id):
    body = request.get_json() or {}
    name = body.get("name")

    if not name:
        return create_api_error_response("Field 'name' is required", 400)

    product = next((p for p in mock_products if p["id"] == product_id), None)
    if not product:
        return create_api_error_response("Product not found", 404)

    product["name"] = name

    return jsonify(create_api_success_response(product))

# CẬP NHẬT MỘT PHẦN product
@app.route('/products/<int:product_id>', methods=['PATCH'])
def update_product_partial(product_id):
    body = request.get_json() or {}

    product = next((p for p in mock_products if p["id"] == product_id), None)
    if not product:
        return create_api_error_response("Product not found", 404)

    # Chỉ update những field có trong body
    if "name" in body:
        product["name"] = body["name"]

    return jsonify(create_api_success_response(product))

# XÓA product
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    global mock_products

    product = next((p for p in mock_products if p["id"] == product_id), None)
    if not product:
        return create_api_error_response("Product not found", 404)

    mock_products = [p for p in mock_products if p["id"] != product_id]

    return jsonify(create_api_success_response({"id": product_id}))   

# Orders – resource khác
@app.route("/orders", methods=["GET"])
def get_orders():
    # Lấy danh sách orders
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    orders = mock_orders
    if status:
        orders = [o for o in orders if o["status"] == status]

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_orders = orders[start:end]

    return jsonify(create_api_success_response(paginated_orders, page, limit, len(orders)))

@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    # Lấy 1 order theo id
    order = next((o for o in mock_orders if o["id"] == order_id), None)

    if not order:
        return create_api_error_response("Order not found", 404)

    return jsonify(create_api_success_response(order))

# Sub-resource: orders của 1 user
@app.route("/users/<int:user_id>/orders", methods=["GET"])
def get_user_orders(user_id):
    # Lấy các orders thuộc về user_id
    user = next((u for u in mock_users if u["id"] == user_id), None)
    if not user:
        return create_api_error_response("User not found", 404)

    user_orders = [o for o in mock_orders if o["userId"] == user_id]

    return jsonify(create_api_success_response(user_orders))


# =================================================

if __name__ == '__main__':
    print(f"API demo running at http://localhost:{port}")
    app.run(port=port)



