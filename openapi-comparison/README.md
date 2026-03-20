# So sánh các format tài liệu hóa API

Dự án demo so sánh 4 format/công cụ tài liệu hóa API phổ biến, áp dụng cho ứng dụng quản lý thư viện đơn giản (Library API).

## Các format được so sánh

| Format | Folder | Mô tả ngắn |
|--------|--------|-----------|
| OpenAPI (Swagger) | `openapi/` | Chuẩn phổ biến nhất, dùng YAML/JSON |
| API Blueprint | `api-blueprint/` | Dùng Markdown, dễ đọc |
| RAML | `RAML/` | YAML-based, mạnh về tái sử dụng |
| TypeSpec | `TypeSpec/` | Ngôn ngữ của Microsoft, compile ra OpenAPI |

## Cấu trúc thư mục

```
openapi-comparison/
├── openapi/          # OpenAPI 3.0 (YAML)
├── api-blueprint/    # API Blueprint (.apib)
├── RAML/             # RAML 1.0
├── TypeSpec/         # TypeSpec -> compile ra OpenAPI
└── codegen/          # Demo sinh code & test từ OpenAPI
```

## So sánh chi tiết

| Tiêu chí | OpenAPI | API Blueprint | RAML | TypeSpec |
|----------|---------|---------------|------|----------|
| Định dạng | YAML/JSON | Markdown | YAML | Ngôn ngữ riêng (.tsp) |
| Độ phổ biến | Rất cao | Trung bình | Trung bình | Thấp (mới) |
| Tool hỗ trợ | Rất nhiều | Vừa | Vừa | Đang phát triển |
| Dễ đọc | Trung bình | Cao | Trung bình | Thấp (cần compile) |
| Sinh code | Có (openapi-generator) | Không | Hạn chế | Có (qua OpenAPI output) |
| Mock server | Có | Có (drakov) | Có | Có (qua OpenAPI output) |
| Tái sử dụng | Có ($ref) | Không | Có (!include) | Có (model/interface) |

## Chạy từng format

```bash
# OpenAPI
cd openapi && npx swagger-ui-watcher openapi.yaml

# API Blueprint
cd api-blueprint && npm install -g aglio && aglio -i api.apib -s

# RAML
cd RAML && npm install -g raml2html && raml2html api.raml > index.html

# TypeSpec
cd TypeSpec && npm install
npx tsp compile main.tsp --emit @typespec/openapi3
npx swagger-ui-watcher tsp-output/@typespec/openapi3/openapi.yaml
```

## Demo sinh code & test


Minh họa phần 2 của bài tập: **sinh code client và test tự động từ OpenAPI spec**.

## 1. Sinh Python client bằng openapi-generator

```bash
npx @openapitools/openapi-generator-cli generate \
  -i ../openapi/openapi.yaml \
  -g python \
  -o generated-client \
  --skip-validate-spec
```

Output: thư mục `generated-client/` chứa toàn bộ Python client được sinh tự động,
gồm models, API classes, configuration, README.

## 2. Chạy test

Đảm bảo server đang chạy (từ `week4/`):

```bash
cd ../../week4
python api/app.py
```

Sau đó chạy test:

```bash
cd ../openapi-comparison/codegen
python test_api.py
```

Kết quả mẫu:

```
=== Library API Tests (generated from OpenAPI spec) ===

  [PASS] GET /books -> 200, 2 books
  [PASS] GET /books/1 -> 200, title=Book 1
  [PASS] GET /books/9999 -> 404, error='Book not found'
  [PASS] POST /books (missing field) -> 400, error='...'
  [PASS] POST /books -> 201, id=3
  [PASS] DELETE /books/3 -> 200

6/6 tests passed.
```
