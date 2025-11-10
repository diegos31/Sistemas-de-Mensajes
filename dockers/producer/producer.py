# producer/producer.py
import pika
import json
import time
import random
import os
import sys

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "secret")
INTERVAL = float(os.getenv("PRODUCE_INTERVAL", 5))

def connect_rabbit():
    creds = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=creds, heartbeat=60, blocked_connection_timeout=30)
    return pika.BlockingConnection(params)

def main():
    backoff = 1
    conn = None
    ch = None
    while True:
        try:
            if not conn or conn.is_closed:
                conn = connect_rabbit()
                ch = conn.channel()
                ch.queue_declare(queue="weather_data", durable=True)
                print("✅ Producer conectado a RabbitMQ")
                backoff = 1

            data = {
                "station_id": random.randint(1, 10),
                "temperature": round(random.uniform(15, 35), 2),
                "humidity": round(random.uniform(20, 95), 2),
                "wind_speed": round(random.uniform(0, 15), 2)
            }
            body = json.dumps(data)
            ch.basic_publish(
                exchange="",
                routing_key="weather_data",
                body=body,
                properties=pika.BasicProperties(content_type="application/json", delivery_mode=2)  # persistent
            )
            print("📤 Enviado:", body)
            time.sleep(INTERVAL)
        except Exception as e:
            print("Producer error:", e, file=sys.stderr)
            try:
                if conn and not conn.is_closed:
                    conn.close()
            except:
                pass
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)

if __name__ == "__main__":
    main()
