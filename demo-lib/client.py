import requests

BASE_URL = "http://127.0.0.1:5000"

def get_books():
    response = requests.get(f"{BASE_URL}/books")
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    books = get_books()
    print(books)
