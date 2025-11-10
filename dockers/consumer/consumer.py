# consumer/consumer.py
import pika
import json
import time
import os
import psycopg2
from psycopg2.extras import Json
import sys

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "secret")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "weatherdb")
POSTGRES_USER = os.getenv("POSTGRES_USER", "weather")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "weatherpass")

def get_pg_conn():
    backoff = 1
    while True:
        try:
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            conn.autocommit = True
            print("✅ Conectado a Postgres")
            return conn
        except Exception as e:
            print("Postgres connection failed:", e, "retrying in", backoff, "s", file=sys.stderr)
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)

def ensure_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS weather (
          id SERIAL PRIMARY KEY,
          station_id INT NOT NULL,
          temperature NUMERIC NOT NULL,
          humidity NUMERIC NOT NULL,
          wind_speed NUMERIC NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS weather_errors (
          id SERIAL PRIMARY KEY,
          payload JSONB,
          error TEXT,
          ts TIMESTAMPTZ DEFAULT now()
        );
        """)
    print("✅ Tablas verificadas/creadas")

def process_message(ch, method, properties, body, pg_conn):
    try:
        payload = json.loads(body)
    except Exception as e:
        print("Invalid JSON:", e, file=sys.stderr)
        with pg_conn.cursor() as cur:
            cur.execute("INSERT INTO weather_errors(payload, error) VALUES (%s,%s)", (Json(body.decode('utf-8', errors='ignore')), str(e)))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Validaciones sencillas
    try:
        temp = float(payload.get("temperature"))
        hum = float(payload.get("humidity"))
        wind = float(payload.get("wind_speed"))
    except Exception as e:
        print("Invalid numeric values:", e, file=sys.stderr)
        with pg_conn.cursor() as cur:
            cur.execute("INSERT INTO weather_errors(payload, error) VALUES (%s,%s)", (Json(payload), f"invalid numeric values: {e}"))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if not (-50 <= temp <= 60):
        reason = f"temperature out of range: {temp}"
        print(reason, file=sys.stderr)
        with pg_conn.cursor() as cur:
            cur.execute("INSERT INTO weather_errors(payload, error) VALUES (%s,%s)", (Json(payload), reason))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Insert into DB
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO weather (station_id, temperature, humidity, wind_speed) VALUES (%s,%s,%s,%s)",
                (payload.get("station_id"), temp, hum, wind)
            )
        print("✅ Guardado en DB:", payload)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("DB insert failed:", e, file=sys.stderr)
        try:
            with pg_conn.cursor() as cur:
                cur.execute("INSERT INTO weather_errors(payload, error) VALUES (%s,%s)", (Json(payload), f"db error: {e}"))
        except:
            pass
        # nack sin requeue para evitar loop
        try:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except:
            pass

def consume():
    pg_conn = get_pg_conn()
    ensure_tables(pg_conn)

    creds = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=creds, heartbeat=60, blocked_connection_timeout=30)

    conn = None
    ch = None
    backoff = 1

    while True:
        try:
            if not conn or conn.is_closed:
                conn = pika.BlockingConnection(params)
                ch = conn.channel()
                ch.queue_declare(queue="weather_data", durable=True)
                ch.basic_qos(prefetch_count=1)
                print("✅ Consumer conectado a RabbitMQ, listo para consumir")
                backoff = 1

            for method_frame, properties, body in ch.consume(queue="weather_data", inactivity_timeout=1):
                if method_frame:
                    process_message(ch, method_frame, properties, body, pg_conn)
            time.sleep(0.1)

        except Exception as e:
            print("Consumer connection error:", e, file=sys.stderr)
            try:
                if conn and not conn.is_closed:
                    conn.close()
            except:
                pass
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)

if __name__ == "__main__":
    consume()
