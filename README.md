# Book API – Week 4 Demo

## Try it live

👉 **[project-ibp8b-reijns0ha-viet2005-68s-projects.vercel.app/docs/](https://project-ibp8b-reijns0ha-viet2005-68s-projects.vercel.app/docs/)**

---

## Endpoints

| Method | URL | Auth | Mô tả |
|--------|-----|------|-------|
| POST | `/auth/login` | ❌ | Đăng nhập, lấy JWT token |
| GET | `/books` | ❌ | Lấy danh sách books (pagination + cookie debug) |
| POST | `/books` | ✅ | Tạo book mới |
| GET | `/books/{id}` | ❌ | Lấy chi tiết 1 book |
| PUT | `/books/{id}` | ✅ | Cập nhật book |
| DELETE | `/books/{id}` | ✅ | Xóa book |

---

## Hướng dẫn demo nhanh

### 1. Đăng nhập lấy token

Vào `POST /auth/login`, nhập:
```json
{ "username": "alice", "password": "123456" }
```
Copy token từ response.

### 2. Authorize

Bấm nút **Authorize** (🔒) góc trên phải, nhập:
```
Bearer <token>
```

### 3. Tạo book mới

Vào `POST /books`, nhập:
```json
{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "year": 2020
}
```

### 4. Demo Cookie debug mode

Truy cập URL sau để set cookie `debug=1` trên trình duyệt:
```
https://project-ibp8b-reijns0ha-viet2005-68s-projects.vercel.app/set-cookie?debug=1
```
Sau đó quay lại `/docs/` và gọi `GET /books` — response sẽ có thêm block `debug`.

---

## Demo users

| Username | Password |
|----------|----------|
| alice | 123456 |
| bob | abcdef |

---

## Chạy local

```bash
pip install -r requirements.txt
python api/app.py
```

Swagger UI: [http://localhost:4001/docs/](http://localhost:4001/docs/)
