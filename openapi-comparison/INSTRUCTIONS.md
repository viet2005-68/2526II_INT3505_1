# Hướng dẫn & Mục tiêu bài tập

## Mục tiêu

1. Hiểu sự khác biệt giữa các format tài liệu hóa API: OpenAPI, API Blueprint, RAML, TypeSpec.
2. Biết cách viết tài liệu API theo từng format cho cùng một ứng dụng.
3. Demo được việc sinh code và test tự động từ file tài liệu API.

## Yêu cầu

- Mỗi format có folder riêng với file tài liệu + README hướng dẫn chạy.
- Tất cả mô tả cùng một API: **Library API** (quản lý sách).
- Có demo sinh code/test từ OpenAPI spec.

## Phương pháp so sánh

Đánh giá theo các tiêu chí:
- **Cú pháp & độ dễ đọc**: Format có dễ viết tay và dễ đọc không?
- **Tool hỗ trợ**: Có Swagger UI, mock server, codegen không?
- **Tái sử dụng**: Có cơ chế chia sẻ schema/component không?
- **Sinh code**: Hỗ trợ generate client/server code không?
- **Độ phổ biến**: Cộng đồng, tài liệu, tích hợp CI/CD.


### [1. OpenAPI (Swagger)](openapi/readme.md)
- Chuẩn công nghiệp, được hỗ trợ rộng rãi nhất.
- Dùng YAML hoặc JSON.
- Swagger UI cho phép test API trực tiếp từ trình duyệt.
- Hỗ trợ sinh code với `openapi-generator`.

### [2. API Blueprint](api-blueprint/README.md)
- Dùng Markdown → dễ đọc như tài liệu thường.
- Công cụ chính: `aglio` (render HTML), `drakov` (mock server).
- Ít tool hỗ trợ sinh code hơn OpenAPI.

### [3. RAML](RAML/README.md)
- YAML-based, có cơ chế `!include` để tái sử dụng.
- Công cụ: `raml2html` (render docs), MuleSoft ecosystem.
- Ít phổ biến hơn OpenAPI trong cộng đồng open source.

### [4. TypeSpec](TypeSpec/README.md)
- Ngôn ngữ của Microsoft, viết như code (type-safe).
- Compile ra OpenAPI → tận dụng toàn bộ hệ sinh thái OpenAPI.
- Phù hợp cho team lớn cần type safety và tái sử dụng cao.
