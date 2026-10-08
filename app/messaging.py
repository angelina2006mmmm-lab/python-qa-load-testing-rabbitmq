"""RabbitMQ publisher; pika is imported lazily to keep isolated unit tests simple."""

import json
import os


def rabbitmq_parameters():
    import pika

    return pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        credentials=pika.PlainCredentials(
            os.getenv("RABBITMQ_USER", "demo"),
            os.getenv("RABBITMQ_PASSWORD", "demo"),
        ),
        heartbeat=30,
        blocked_connection_timeout=3,
        socket_timeout=3,
        connection_attempts=3,
        retry_delay=1,
    )


def publish_job(job_id: str, message: str) -> None:
    import pika

    conn = pika.BlockingConnection(rabbitmq_parameters())
    try:
        ch = conn.channel()
        ch.queue_declare(queue=os.getenv("QUEUE_NAME", "premium_notifications"), durable=True)
        ch.confirm_delivery()
        ch.basic_publish(
            exchange="",
            routing_key=os.getenv("QUEUE_NAME", "premium_notifications"),
            body=json.dumps({"id": job_id, "message": message}, ensure_ascii=False).encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
            mandatory=True,
        )
    finally:
        if conn.is_open:
            conn.close()
