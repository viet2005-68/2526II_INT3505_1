"""
Week 12: API as a Product
Demo: Developer Portal — API key management, freemium quota, analytics, sandbox

Chạy : python app.py
Portal: mở developer-portal/index.html trong trình duyệt
Admin : X-Admin-Key: admin-secret-key  →  GET /admin/analytics
"""

from flask import Flask, request, jsonify, make_response, g
from datetime import datetime, date
from collections import defaultdict
import secrets
import time

app = Flask(__name__)

# ══════════════════════════════════════════════
# 1. PRICING PLANS  (Freemium model)
# ══════════════════════════════════════════════

PLANS = {
    "free": {
        "name": "Free",
        "price_usd": 0,
        "daily_quota": 100,
        "rate_limit_rpm": 10,
        "sla": None,
        "support": "Community",
        "features": ["100 calls/ngày", "Sandbox access", "Community support"],
    },
    "pro": {
        "name": "Pro",
        "price_usd": 29,
        "daily_quota": 10_000,
        "rate_limit_rpm": 200,
        "sla": "99.9%",
        "support": "Email (24h)",
        "features": ["10,000 calls/ngày", "SLA 99.9%", "Email support", "Search API", "Analytics"],
    },
    "enterprise": {
        "name": "Enterprise",
        "price_usd": 299,
        "daily_quota": None,          # Unlimited
        "rate_limit_rpm": 2000,
        "sla": "99.99%",
        "support": "24/7 Priority",
        "features": ["Unlimited calls", "SLA 99.99%", "24/7 Priority support",
                     "Custom rate limits", "Dedicated account manager", "SLA credits"],
    },
}

# ══════════════════════════════════════════════
# 2. IN-MEMORY STORES
# ══════════════════════════════════════════════

developers_db = {}      # email → developer record
api_keys_db = {}        # api_key → developer record (same object)
rate_limit_history = defaultdict(list)  # api_key → list of timestamps


def _make_dev(email: str, name: str, plan: str) -> dict:
    key = f"sk_{secrets.token_hex(16)}"
    dev = {
        "email":       email,
        "name":        name,
        "plan":        plan,
        "api_key":     key,
        "created_at":  datetime.utcnow().isoformat() + "Z",
        "daily_usage": defaultdict(int),   # date → call count
        "total_calls": 0,
        "error_calls": 0,
    }
    developers_db[email] = dev
    api_keys_db[key]     = dev
    return dev


# Seed demo data
_make_dev("alice@example.com", "Alice",  "pro")
_make_dev("bob@example.com",   "Bob",    "free")
_make_dev("carol@example.com", "Carol",  "enterprise")


# ══════════════════════════════════════════════
# 3. ANALYTICS TRACKER  (KPIs)
# ══════════════════════════════════════════════

class Analytics:
    def __init__(self):
        self.total_calls = 0
        self.error_calls = 0
        self.calls_by_endpoint = defaultdict(int)
        self.calls_by_plan = defaultdict(int)
        self.start_time = time.time()

    def record(self, endpoint: str, plan: str, is_error: bool):
        self.total_calls += 1
        if is_error:
            self.error_calls += 1
        self.calls_by_endpoint[endpoint] += 1
        self.calls_by_plan[plan] += 1

    def kpis(self) -> dict:
        today = date.today().isoformat()
        active = sum(1 for d in developers_db.values() if d["daily_usage"][today] > 0)
        top_eps = sorted(self.calls_by_endpoint.items(), key=lambda x: x[1], reverse=True)[:5]
        mrr = sum(PLANS[d["plan"]]["price_usd"] for d in developers_db.values())
        return {
            "registered_developers": len(developers_db),
            "active_developers_today": active,
            "total_api_calls": self.total_calls,
            "error_rate_percent": round(self.error_calls / max(self.total_calls, 1) * 100, 2),
            "calls_by_plan": dict(self.calls_by_plan),
            "top_endpoints": [{"endpoint": e, "calls": c} for e, c in top_eps],
            "monthly_recurring_revenue_usd": mrr,
            "uptime_seconds": int(time.time() - self.start_time),
        }


analytics = Analytics()


# ══════════════════════════════════════════════
# 4. AUTH & LIMITS MIDDLEWARE / HELPERS
# ══════════════════════════════════════════════

def check_limits_and_key():
    x_api_key = request.headers.get("X-API-Key")
    if not x_api_key:
        return None, {
            "error":   "MISSING_API_KEY",
            "message": "API key bị thiếu. Hãy truyền header X-API-Key."
        }, 401

    if x_api_key not in api_keys_db:
        return None, {
            "error":   "INVALID_API_KEY",
            "message": "API key không hợp lệ.",
            "hint":    "Đăng ký miễn phí tại POST /developers/register",
        }, 401

    dev   = api_keys_db[x_api_key]
    plan  = PLANS[dev["plan"]]
    today = date.today().isoformat()
    quota = plan["daily_quota"]
    used  = dev["daily_usage"][today]

    # Check Daily Quota
    if quota is not None and used >= quota:
        return None, {
            "error":       "QUOTA_EXCEEDED",
            "message":     f"Đã dùng hết {quota} calls/ngày của plan {dev['plan'].upper()}.",
            "used":        used,
            "limit":       quota,
            "reset_at":    f"{today}T23:59:59Z",
            "upgrade_url": "POST /developers/upgrade",
        }, 429

    # Check Rate Limit (RPM)
    now = time.time()
    rpm_limit = plan["rate_limit_rpm"]
    
    # Filter out timestamps older than 60s
    history = rate_limit_history[x_api_key]
    rate_limit_history[x_api_key] = [t for t in history if now - t < 60]
    
    if len(rate_limit_history[x_api_key]) >= rpm_limit:
        return None, {
            "error": "RATE_LIMIT_EXCEEDED",
            "message": f"Rate limit exceeded. Maximum {rpm_limit} RPM for plan '{plan['name']}'. Please wait."
        }, 429

    # Track current call timestamp for rate limiting
    rate_limit_history[x_api_key].append(now)
    return dev, None, 200


def require_admin():
    x_admin_key = request.headers.get("X-Admin-Key")
    if x_admin_key != "admin-secret-key":
        return jsonify({"error": "Admin access only. Header: X-Admin-Key"}), 403
    return None


@app.before_request
def before_request_func():
    g.start_time = time.time()
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        return response


@app.after_request
def after_request_func(response):
    # Calculate response latency
    if hasattr(g, 'start_time'):
        latency_ms = (time.time() - g.start_time) * 1000
        response.headers["X-Response-Time"] = f"{latency_ms:.1f}ms"

    # Set generic CORS headers for filesystem double-click HTML loading
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"

    # Middleware: Track statistics on actual API endpoints
    if request.path.startswith("/api/v1/"):
        api_key = request.headers.get("X-API-Key")
        if api_key and api_key in api_keys_db:
            dev = api_keys_db[api_key]
            today = date.today().isoformat()
            dev["daily_usage"][today] += 1
            dev["total_calls"] += 1
            is_err = response.status_code >= 400
            if is_err:
                dev["error_calls"] += 1
            analytics.record(request.path, dev["plan"], is_err)

    return response


# ══════════════════════════════════════════════
# 5. DEVELOPER PORTAL ENDPOINTS
# ══════════════════════════════════════════════

@app.route("/", methods=["GET"])
def api_home():
    """Trang chủ API — hướng dẫn bắt đầu nhanh."""
    return jsonify({
        "name":    "Book API v1.0",
        "tagline": "Fast, reliable book catalog API",
        "quick_start": [
            "1. POST /developers/register  → nhận api_key",
            "2. GET /api/v1/books  với header X-API-Key: sk_...",
            "3. GET /sandbox/books  để test không cần key",
        ],
        "links": {"docs": "/docs", "plans": "/plans", "sandbox": "/sandbox/books"},
    })


@app.route("/plans", methods=["GET"])
def list_plans():
    """Xem bảng giá — Free, Pro, Enterprise."""
    return jsonify({
        "plans": PLANS,
        "note": "Free plan không cần credit card. Nâng cấp bất cứ lúc nào.",
    })


@app.route("/developers/register", methods=["POST"])
def register():
    """Đăng ký developer account — nhận API key ngay lập tức."""
    body = request.json or {}
    email = body.get("email")
    name = body.get("name")
    plan = body.get("plan", "free")

    if not email or not name:
        return jsonify({"error": "MISSING_FIELDS", "message": "Email và Tên là bắt buộc."}), 400

    if email in developers_db:
        return jsonify({
            "error":   "EMAIL_EXISTS",
            "message": "Email đã đăng ký.",
            "hint":    f"Xem key tại GET /developers/{email}/usage",
        }), 409

    if plan not in PLANS:
        return jsonify({"error": "INVALID_PLAN", "valid": list(PLANS.keys())}), 400

    dev  = _make_dev(email, name, plan)
    info = PLANS[plan]
    return jsonify({
        "message":    f"Chào mừng {name}! API key đã sẵn sàng.",
        "api_key":    dev["api_key"],
        "plan":       plan,
        "daily_quota": info["daily_quota"] or "Unlimited",
        "quick_start": f'curl -H "X-API-Key: {dev["api_key"]}" http://localhost:8000/api/v1/books',
    }), 201


@app.route("/developers/<email>/usage", methods=["GET"])
def get_usage(email):
    """Xem usage, quota còn lại và lịch sử theo ngày."""
    if email not in developers_db:
        return jsonify({"error": "NOT_FOUND", "message": "Developer not found"}), 404

    dev   = developers_db[email]
    plan  = PLANS[dev["plan"]]
    today = date.today().isoformat()
    used  = dev["daily_usage"][today]
    quota = plan["daily_quota"]

    return jsonify({
        "email":   email,
        "name":    dev["name"],
        "plan":    dev["plan"],
        "api_key": dev["api_key"],
        "today": {
            "used":          used,
            "quota":         quota or "Unlimited",
            "remaining":     (quota - used) if quota else "Unlimited",
            "percent_used":  round(used / quota * 100, 1) if quota else 0,
        },
        "all_time": {
            "total_calls": dev["total_calls"],
            "error_calls": dev["error_calls"],
            "error_rate":  round(dev["error_calls"] / max(dev["total_calls"], 1) * 100, 2),
        },
        "daily_history": dict(dev["daily_usage"]),
    })


@app.route("/developers/upgrade", methods=["POST"])
def upgrade_plan():
    """Nâng cấp plan — mô hình subscription."""
    body = request.json or {}
    email = body.get("email")
    new_plan = body.get("new_plan")

    if not email or not new_plan:
        return jsonify({"error": "MISSING_FIELDS", "message": "Email và new_plan là bắt buộc."}), 400

    if email not in developers_db:
        return jsonify({"error": "NOT_FOUND", "message": "Developer not found"}), 404
        
    if new_plan not in PLANS:
        return jsonify({"error": "INVALID_PLAN", "valid_plans": list(PLANS.keys())}), 400

    dev      = developers_db[email]
    old_plan = dev["plan"]
    dev["plan"] = new_plan
    info = PLANS[new_plan]

    return jsonify({
        "message":     f"Nâng cấp thành công: {old_plan.upper()} → {new_plan.upper()}",
        "new_plan":    new_plan,
        "daily_quota": info["daily_quota"] or "Unlimited",
        "price":       f"${info['price_usd']}/tháng",
        "sla":         info["sla"] or "Không có SLA",
        "new_features": info["features"],
    })


# ══════════════════════════════════════════════
# SANDBOX  (không cần key, không tốn quota)
# ══════════════════════════════════════════════

@app.route("/sandbox/books", methods=["GET"])
def sandbox_books():
    """Sandbox: Xem data sách mẫu không cần API key."""
    return jsonify({
        "sandbox": True,
        "warning": "Data này là mẫu — không phản ánh data thực",
        "data": [
            {"id": "demo_001", "title": "[DEMO] To Kill a Mockingbird", "author": "Harper Lee", "year": 1960},
            {"id": "demo_002", "title": "[DEMO] 1984",                  "author": "George Orwell", "year": 1949},
        ],
        "get_real_data": "POST /developers/register để nhận API key miễn phí",
    })


@app.route("/sandbox/echo", methods=["POST"])
def sandbox_echo():
    """Sandbox echo: gửi bất kỳ payload nào, nhận lại nguyên vẹn."""
    try:
        body = request.json
    except Exception:
        body = None
    return jsonify({
        "sandbox":   True,
        "echo":      body,
        "headers":   dict(request.headers),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })


# ══════════════════════════════════════════════
# API v1  (cần API key + quota) — BOOK API
# ══════════════════════════════════════════════

_BOOKS = [
    {"id": "b001", "title": "To Kill a Mockingbird", "author": "Harper Lee",        "year": 1960, "genre": "fiction"},
    {"id": "b002", "title": "1984",                  "author": "George Orwell",      "year": 1949, "genre": "dystopia"},
    {"id": "b003", "title": "The Great Gatsby",       "author": "F. Scott Fitzgerald","year": 1925, "genre": "fiction"},
    {"id": "b004", "title": "Sapiens",                "author": "Yuval Noah Harari",  "year": 2011, "genre": "non-fiction"},
    {"id": "b005", "title": "Clean Code",             "author": "Robert C. Martin",   "year": 2008, "genre": "tech"},
]


def _quota_headers(dev: dict):
    today = date.today().isoformat()
    quota = PLANS[dev["plan"]]["daily_quota"]
    used  = dev["daily_usage"][today]
    return {
        "X-Plan":             dev["plan"],
        "X-Quota-Limit":      str(quota) if quota else "Unlimited",
        "X-Quota-Remaining":  str(max(0, quota - used)) if quota else "Unlimited",
    }


@app.route("/api/v1/books", methods=["GET"])
def get_books():
    """Lấy danh sách sách — yêu cầu API key."""
    dev, err, status = check_limits_and_key()
    if err:
        return jsonify(err), status
        
    resp = make_response(jsonify({"data": _BOOKS, "count": len(_BOOKS)}))
    for k, v in _quota_headers(dev).items():
        resp.headers[k] = v
    return resp


@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id):
    """Lấy chi tiết 1 cuốn sách — yêu cầu API key."""
    dev, err, status = check_limits_and_key()
    if err:
        return jsonify(err), status

    book = next((b for b in _BOOKS if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "NOT_FOUND", "message": "Book not found"}), 404

    resp = make_response(jsonify(book))
    for k, v in _quota_headers(dev).items():
        resp.headers[k] = v
    return resp


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    """Thêm sách mới vào catalog — yêu cầu API key."""
    dev, err, status = check_limits_and_key()
    if err:
        return jsonify(err), status

    body = request.json or {}
    title = body.get("title")
    author = body.get("author")
    year = body.get("year")
    genre = body.get("genre", "fiction")

    if not title or not author or not year:
        return jsonify({"error": "MISSING_FIELDS", "message": "Tiêu đề, Tác giả và Năm xuất bản là bắt buộc."}), 400

    new_id = f"b{len(_BOOKS)+1:03d}"
    new_book = {
        "id":     new_id,
        "title":  title,
        "author": author,
        "year":   year,
        "genre":  genre,
    }
    _BOOKS.append(new_book)

    resp = make_response(jsonify({
        "message": f"Đã thêm sách '{title}' thành công.",
        "data":    new_book,
    }))
    for k, v in _quota_headers(dev).items():
        resp.headers[k] = v
    return resp, 201


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    """Xóa sách khỏi catalog — yêu cầu API key."""
    dev, err, status = check_limits_and_key()
    if err:
        return jsonify(err), status

    global _BOOKS
    book = next((b for b in _BOOKS if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "NOT_FOUND", "message": "Book not found"}), 404

    _BOOKS = [b for b in _BOOKS if b["id"] != book_id]

    resp = make_response(jsonify({"message": f"Đã xóa sách '{book['title']}' thành công."}))
    for k, v in _quota_headers(dev).items():
        resp.headers[k] = v
    return resp


@app.route("/api/v1/search", methods=["GET"])
def search():
    """Tìm kiếm sách — chỉ Pro & Enterprise (Feature Gating)."""
    dev, err, status = check_limits_and_key()
    if err:
        return jsonify(err), status

    if dev["plan"] == "free":
        return jsonify({
            "error":        "FEATURE_LOCKED",
            "message":      "Search API chỉ dành cho Pro và Enterprise.",
            "current_plan": "free",
            "upgrade_to":   "pro",
            "upgrade_url":  "POST /developers/upgrade",
            "pro_price":    "$29/tháng",
        }), 403

    q = request.args.get("q", "")
    results = [b for b in _BOOKS if q.lower() in b["title"].lower() or q.lower() in b["author"].lower()]
    
    resp = make_response(jsonify({"data": results, "query": q, "count": len(results)}))
    for k, v in _quota_headers(dev).items():
        resp.headers[k] = v
    return resp


# ══════════════════════════════════════════════
# ADMIN ANALYTICS  (KPI Dashboard)
# ══════════════════════════════════════════════

@app.route("/admin/analytics", methods=["GET"])
def admin_analytics():
    """KPI Dashboard — chỉ admin."""
    err_resp = require_admin()
    if err_resp:
        return err_resp
    return jsonify(analytics.kpis())


@app.route("/admin/developers", methods=["GET"])
def admin_developers():
    """Danh sách developers, usage và doanh thu mỗi account."""
    err_resp = require_admin()
    if err_resp:
        return err_resp

    today = date.today().isoformat()
    rows  = []
    for dev in developers_db.values():
        rows.append({
            "email":         dev["email"],
            "name":          dev["name"],
            "plan":          dev["plan"],
            "created_at":    dev["created_at"],
            "calls_today":   dev["daily_usage"][today],
            "total_calls":   dev["total_calls"],
            "monthly_rev_usd": PLANS[dev["plan"]]["price_usd"],
        })
    rows.sort(key=lambda x: x["total_calls"], reverse=True)
    return jsonify({
        "total":      len(rows),
        "total_mrr":  sum(r["monthly_rev_usd"] for r in rows),
        "developers": rows,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
