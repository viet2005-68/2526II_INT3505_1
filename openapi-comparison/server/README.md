# Server – Library API Demo

Server Flask đơn giản phục vụ demo cho các format tài liệu hóa API.

## Endpoints

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/books` | Lấy danh sách tất cả sách |
| GET | `/books/{id}` | Lấy chi tiết 1 cuốn sách theo ID |

## Chạy server

```bash
pip install -r requirements.txt
python app.py
```

Server chạy tại: http://localhost:4001

## Test nhanh

```bash
# Lấy tất cả sách
curl http://localhost:4001/books

# Lấy sách theo ID
curl http://localhost:4001/books/1

# ID không tồn tại
curl http://localhost:4001/books/999
```
