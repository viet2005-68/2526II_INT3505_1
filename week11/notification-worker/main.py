import pika, json, time, os
from pika.exceptions import AMQPConnectionError

RABBIT_URL = os.environ.get("RABBIT_URL")


def connect_rabbitmq(url, retries=10, delay=5):
    """Hàm thử kết nối lại nhiều lần cho đến khi RabbitMQ sẵn sàng"""
    for i in range(retries):
        try:
            params = pika.URLParameters(url)
            connection = pika.BlockingConnection(params)
            print("Connected to RabbitMQ")
            return connection
        except AMQPConnectionError as e:
            print(f"RabbitMQ chưa sẵn sàng... Đang thử lại {i+1}/{retries}")
            time.sleep(delay)
    raise Exception("Không thể kết nối RabbitMQ sau nhiều lần thử")

connection = connect_rabbitmq(RABBIT_URL)
channel = connection.channel()

channel.queue_declare(queue='notifications', durable=True)
print(" [*] Notification worker started. Waiting for messages.")

def callback(ch, method, properties, body):
    # Du lieu tu RabbitMQ gui dang bytes, nen can dung json.loads de dich lai
    event = json.loads(body)
    print("Process message:", event)

    # Demo time to send message
    time.sleep(1);
    print(f" [✓] Gửi Notification thành công cho event_id={event.get('id')}")

    ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_qos(prefetch_count=1)

# Chỉ lấy 1 message một lúc để xử lý tốn tài nguyên
channel.basic_qos(prefetch_count=1)

# Đăng ký hàm callback ở trên với hàng đợi 'notifications'
channel.basic_consume(queue='notifications', on_message_callback=callback)

# Bắt đầu vòng lặp vô tận
channel.start_consuming()
