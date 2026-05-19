import hashlib
import hmac
import json
import os
import time


import pika
from flask import Flask, jsonify, request, abort

app = Flask(__name__)
RABBIT_URL = os.environ.get("RABBIT_URL", "amqp://admin:admin@rabbitmq:5672/")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "webhook_secret")
QUEUE_NAME = "notifications"

def verify_signature(payload_body, signature):
    """Verify HMAC SHA256 signature"""
    computed_sig = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_sig, signature)



@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload_body = request.data
    signature = request.headers['X-Signature']

    if not signature or not verify_signature(payload_body, signature):
        abort(401, description='Signature verification failed')

    payload = json.loads(request.data)

    params = pika.URLParameters(RABBIT_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    #push message into queue
    channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=json.dumps(payload), properties=pika.BasicProperties(delivery_mode=2))

    connection.close()

    return jsonify({"status": "ok"}), 200



@app.route("/")
def health():
    return "Webhook server OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
