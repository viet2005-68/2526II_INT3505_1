import requests

BASE_URL = "http://127.0.0.1:5000"

def get_books():
    response = requests.get(f"{BASE_URL}/books")
    response.raise_for_status()
    return response.json()


def demo_stateless():
    """
    Demo Stateless: Mỗi request độc lập, KHÔNG dùng session/cookie.
    Server không lưu state giữa các request.
    """
    print("=== DEMO STATELESS ===\n")
    
    # Request 1
    r1 = requests.get(f"{BASE_URL}/demo-stateless")
    data1 = r1.json()
    print(f"Request 1: request_id = {data1['request_id']}")
    
    # Request 2 - KHÔNG gửi session, KHÔNG cookie
    r2 = requests.get(f"{BASE_URL}/demo-stateless")
    data2 = r2.json()
    print(f"Request 2: request_id = {data2['request_id']}")
    
    # Request 3
    r3 = requests.get(f"{BASE_URL}/demo-stateless")
    data3 = r3.json()
    print(f"Request 3: request_id = {data3['request_id']}")
    
    print(f"\n→ Mỗi request_id KHÁC NHAU = Server KHÔNG lưu state")
    print(f"→ Mỗi request xử lý ĐỘC LẬP, không phụ thuộc request trước")
    print(f"→ Client KHÔNG gửi session/cookie, server vẫn xử lý được")


def demo_cacheable():
    """
    Demo Cacheable: Response có Cache-Control header.
    Request 1 và 2 - kiểm tra header Cache-Control.
    """
    print("=== DEMO CACHEABLE ===\n")
    
    r = requests.get(f"{BASE_URL}/books-cacheable")
    data = r.json()
    
    print(f"Data: {data}")
    print(f"\nHeaders từ server:")
    print(f"  Cache-Control: {r.headers.get('Cache-Control', 'N/A')}")
    print(f"  X-Cache-Info: {r.headers.get('X-Cache-Info', 'N/A')}")
    print(f"\n→ Client/Browser có thể cache response 60 giây")
    print(f"→ Request tiếp theo trong 60s có thể dùng cache, không cần gọi server")


def get_books_no_session():
    """GET books - Stateless: Không cần login, session, cookie."""
    response = requests.get(f"{BASE_URL}/books")
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stateless":
        demo_stateless()
    elif len(sys.argv) > 1 and sys.argv[1] == "cacheable":
        demo_cacheable()
    else:
        books = get_books()
        print(books)
