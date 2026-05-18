import json
import os
import time

import pika
from flask import Flask, jsonify, request

app = Flask(__name__)
RABBIT_URL = os.environ.get("RABBIT_URL", "amqp://admin:admin@rabbitmq:5672/")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "webhook_secret")
QUEUE_NAME = "notifications"


def publish_message(payload: dict) -> None:
    parameters = pika.URLParameters(RABBIT_URL)
    last_error = None
    for _ in range(10):
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=QUEUE_NAME,
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            connection.close()
            return
        except pika.exceptions.AMQPError as error:
            last_error = error
            time.sleep(2)
    raise last_error


@app.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@app.post("/webhook")
def handle_webhook():
    if request.headers.get("X-Webhook-Secret") != WEBHOOK_SECRET:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid json"}), 400

    publish_message(payload)
    return jsonify({"status": "queued"}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
