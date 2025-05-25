# Business Model Canvas – Book API

> Áp dụng khung Business Model Canvas (BMC) của Alexander Osterwalder cho **Book API** – REST API quản lý danh sách sách với JWT auth, CRUD, webhook và Swagger UI.

---

## 1. Customer Segments (Phân khúc khách hàng)

| Phân khúc | Mô tả |
|-----------|-------|
| **Indie developers** | Lập trình viên cá nhân xây dựng app đọc sách, blog văn học |
| **EdTech startups** | Các startup giáo dục cần catalog sách để tích hợp vào LMS |
| **E-commerce platforms** | Sàn thương mại điện tử bán sách cần dữ liệu sách chuẩn hóa |
| **Library systems** | Thư viện số cần API để quản lý và tra cứu đầu sách |
| **Mobile app developers** | Nhà phát triển app iOS/Android cần backend sẵn có |

---

## 2. Value Propositions (Giá trị cốt lõi)

- 📚 **Catalog sách chuẩn hóa**: Dữ liệu sách nhất quán (title, author, year, ISBN)
- 🔒 **Bảo mật JWT**: Authentication sẵn có, không cần tự build auth
- ⚡ **Tích hợp nhanh**: Swagger UI, OpenAPI spec, sandbox môi trường thử ngay
- 🔔 **Webhook real-time**: Nhận notification khi có thay đổi dữ liệu (thêm/xóa sách)
- 📖 **Developer-first**: Tài liệu rõ ràng, code example đầy đủ, onboarding < 5 phút

---

## 3. Channels (Kênh tiếp cận)

| Kênh | Mục đích |
|------|----------|
| **Developer Portal** | Đăng ký API key, đọc docs, thử sandbox |
| **GitHub** | Mã nguồn mở, issue tracker, community |
| **RapidAPI / API Marketplace** | Distribution để tiếp cận developer toàn cầu |
| **Blog & Tech articles** | Hướng dẫn tích hợp, use-case thực tế |
| **Twitter/X & Dev.to** | Marketing kỹ thuật, cập nhật tính năng |

---

## 4. Customer Relationships (Quan hệ khách hàng)

- **Self-service**: Developer tự đăng ký, đọc docs và bắt đầu dùng API ngay
- **Automated onboarding**: Email chào mừng + hướng dẫn 5 bước đầu tiên
- **Community forum**: GitHub Discussions / Discord cho Q&A
- **SLA support**: Hỗ trợ email trong 24h cho gói trả phí
- **Changelog & Status page**: Thông báo downtime, breaking changes minh bạch

---

## 5. Revenue Streams (Dòng doanh thu)

### Mô hình Freemium

| Tier | Giới hạn | Giá |
|------|----------|-----|
| **Free** | 1,000 calls/tháng, 1 API key | $0 |
| **Starter** | 50,000 calls/tháng, 3 API key, webhook | $9/tháng |
| **Pro** | 500,000 calls/tháng, 10 API key, analytics | $49/tháng |
| **Enterprise** | Unlimited, SLA 99.9%, dedicated support | Liên hệ |

### Mô hình Pay-per-call (thay thế / bổ sung)

| Dải | Đơn giá |
|-----|---------|
| 0 – 10,000 calls | $0 (free tier) |
| 10,001 – 100,000 calls | $0.0005 / call |
| 100,001+ calls | $0.0003 / call (volume discount) |

---

## 6. Key Resources (Nguồn lực chính)

- **Codebase**: FastAPI/Python backend, PostgreSQL database
- **Infrastructure**: Cloud hosting (Vercel + Railway hoặc AWS)
- **Documentation**: OpenAPI spec, Swagger UI, Postman collection
- **Developer Portal**: Trang web quản lý API key, theo dõi usage
- **Nhân lực**: 2-3 developer duy trì, 1 technical writer

---

## 7. Key Activities (Hoạt động chính)

- 🔧 **Phát triển & bảo trì API**: Thêm tính năng, fix bug, versioning
- 📝 **Viết & cập nhật documentation**: Docs luôn đồng bộ với code
- 📊 **Monitor & analytics**: Theo dõi uptime, latency, error rate
- 🤝 **Developer relations**: Hỗ trợ community, viết blog, tham gia hackathon
- 🔐 **Security**: Rate limiting, API key rotation, audit log

---

## 8. Key Partners (Đối tác chính)

| Đối tác | Vai trò |
|---------|---------|
| **Cloud providers** (AWS/GCP) | Hạ tầng hosting, CDN, database |
| **Auth0 / Firebase** | Identity provider nếu mở rộng OAuth2 |
| **RapidAPI** | API marketplace để phân phối |
| **Open Library / Google Books** | Nguồn dữ liệu sách bổ sung |
| **Stripe / PayPal** | Xử lý thanh toán subscription |

---

## 9. Cost Structure (Cơ cấu chi phí)

| Khoản mục | Chi phí ước tính |
|-----------|-----------------|
| Cloud hosting & database | $20–100/tháng |
| CDN & bandwidth | $5–30/tháng |
| Monitoring tools (Datadog/Grafana) | $0–50/tháng |
| Domain & SSL | $15/năm |
| Developer time | Chi phí lớn nhất |

---

## 10. KPIs – Chỉ số đo lường

| KPI | Mục tiêu (6 tháng đầu) | Đo bằng |
|-----|------------------------|---------|
| **Số developer đăng ký** | 500 accounts | Database users table |
| **Monthly Active Developers** | 100 MAD | API key có ≥ 1 call/tháng |
| **Call Volume** | 1M calls/tháng | API gateway logs |
| **Error Rate** | < 1% | 5xx responses / total requests |
| **Average Latency** | < 200ms (p95) | APM tool |
| **Conversion Free → Paid** | > 5% | Stripe subscription data |
| **Churn Rate** | < 10%/tháng | Subscription cancellations |
| **Time to First Call** | < 10 phút | Signup → first API call timestamp |

---

## 11. Chiến lược ra mắt API (Go-to-Market)

### Phase 1 – Beta (Tháng 1–2)
- [ ] Deploy Developer Portal với đăng ký API key
- [ ] Publish OpenAPI spec lên Swagger Hub
- [ ] Mời 20 developer thử nghiệm (closed beta)
- [ ] Thu thập feedback, fix bugs

### Phase 2 – Launch (Tháng 3)
- [ ] Public launch trên RapidAPI
- [ ] Blog post "Building a Book App in 15 minutes with Book API"
- [ ] Submit lên các newsletter: Hacker News, DevTo, Reddit r/webdev

### Phase 3 – Growth (Tháng 4–6)
- [ ] Bật tính năng analytics cho developers
- [ ] Ra mắt tier trả phí (Starter & Pro)
- [ ] Tích hợp webhook marketplace

---

## Tóm tắt Canvas (1 trang)

```
┌─────────────────┬────────────────────┬─────────────────────┬──────────────────┐
│  KEY PARTNERS   │  KEY ACTIVITIES    │  VALUE PROPOSITIONS │ CUSTOMER         │
│                 │                    │                     │ RELATIONSHIPS    │
│ • AWS/GCP       │ • API development  │ • Catalog chuẩn hóa │ • Self-service   │
│ • RapidAPI      │ • Documentation    │ • JWT auth sẵn có   │ • Community      │
│ • Open Library  │ • Dev relations    │ • Webhook real-time │ • SLA support    │
│ • Stripe        │ • Security/ops     │ • Onboard < 5 phút  │                  │
│                 ├────────────────────┤                     ├──────────────────┤
│                 │  KEY RESOURCES     │                     │ CHANNELS         │
│                 │                    │                     │                  │
│                 │ • Codebase (Python)│                     │ • Dev Portal     │
│                 │ • API Docs         │                     │ • GitHub         │
│                 │ • Infrastructure   │                     │ • RapidAPI       │
│                 │ • Dev team         │                     │ • Blog/Social    │
├─────────────────┴────────────────────┴─────────────────────┴──────────────────┤
│  COST STRUCTURE                      │  REVENUE STREAMS                        │
│                                      │                                          │
│  • Cloud hosting: $20–100/mo         │  • Freemium: Free / $9 / $49 / Custom   │
│  • Monitoring: $0–50/mo              │  • Pay-per-call: $0.0005/call           │
│  • Developer time (main cost)        │  • Enterprise contracts                  │
└──────────────────────────────────────┴──────────────────────────────────────────┘
```
