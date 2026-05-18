import json
import os
import time

import pika

RABBIT_URL = os.environ.get("RABBIT_URL", "amqp://admin:admin@rabbitmq:5672/")
QUEUE_NAME = "notifications"


def handle_message(ch, method, properties, body):
    payload = json.loads(body.decode())
    print(f"Processed notification: {payload}", flush=True)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    parameters = pika.URLParameters(RABBIT_URL)
    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)
            print("Waiting for notifications", flush=True)
            channel.start_consuming()
        except pika.exceptions.AMQPError:
            time.sleep(2)


if __name__ == "__main__":
    main()
