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


def get_books_no_session():
    """GET books - Stateless: Không cần login, session, cookie."""
    response = requests.get(f"{BASE_URL}/books")
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stateless":
        demo_stateless()
    else:
        books = get_books()
        print(books)
