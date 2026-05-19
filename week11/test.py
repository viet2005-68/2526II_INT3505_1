import hashlib
import hmac
import json
from urllib import request, error

WEBHOOK_SECRET = "webhook_secret"
payload = {
    "id": "evt_01",
    "type": "payment.succeeded",
    "user_id": 123,
}
payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
signature = hmac.new(WEBHOOK_SECRET.encode(), payload_bytes, hashlib.sha256).hexdigest()

headers = {
    "Content-Type": "application/json",
    "X-Signature": signature,
}

if __name__ == "__main__":
    req = request.Request(
        "http://localhost:5000/webhook",
        data=payload_bytes,
        headers=headers,
        method="POST",
    )
    try:
        with request.urlopen(req) as resp:
            print(resp.status, resp.read().decode())
    except error.HTTPError as resp:
        print(resp.code, resp.read().decode())
