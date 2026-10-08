"""RabbitMQ consumer: process a queued mock notification and persist the result."""

import json
import logging
import os
import time

from app.db import init_db, update_job
from app.messaging import rabbitmq_parameters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def process_message(body: bytes) -> str:
    payload = json.loads(body)
    job_id = payload["id"]
    if not isinstance(job_id, str) or not isinstance(payload["message"], str):
        raise ValueError("Invalid payload")
    update_job(job_id, "processing")
    # Demo processing; no real customer data or MTS systems are used.
    time.sleep(0.02)
    update_job(job_id, "done", "Processed mock notification")
    return job_id


def consume() -> None:
    import pika

    init_db()
    queue = os.getenv("QUEUE_NAME", "premium_notifications")
    while True:
        try:
            conn = pika.BlockingConnection(rabbitmq_parameters())
            ch = conn.channel()
            ch.queue_declare(queue=queue, durable=True)
            ch.basic_qos(prefetch_count=10)

            def on_message(channel, method, _properties, body):
                try:
                    job_id = process_message(body)
                    logger.info("Processed job: %s", job_id)
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                except Exception:
                    logger.exception("Failed to process message")
                    try:
                        payload = json.loads(body)
                        if isinstance(payload.get("id"), str):
                            update_job(payload["id"], "failed", "Worker processing error")
                    except (ValueError, KeyError, TypeError):
                        pass
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            ch.basic_consume(queue=queue, on_message_callback=on_message)
            logger.info("Waiting for messages on %s", queue)
            ch.start_consuming()
        except (pika.exceptions.AMQPError, OSError):
            logger.exception("RabbitMQ connection lost; retrying in 3 seconds")
            time.sleep(3)


if __name__ == "__main__":
    consume()
