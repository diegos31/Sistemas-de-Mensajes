import pika
import psycopg2
import json
import os
import time

# Espera para que la base de datos esté lista
time.sleep(10)

# Conexión a RabbitMQ
rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
rabbit_user = os.getenv("RABBITMQ_USER", "admin")
rabbit_pass = os.getenv("RABBITMQ_PASS", "secret")

credentials = pika.PlainCredentials(rabbit_user, rabbit_pass)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_host, credentials=credentials)
)
channel = connection.channel()

channel.queue_declare(queue="weather_data", durable=True)
print("✅ Consumidor conectado a RabbitMQ. Esperando mensajes...")

# Conexión a PostgreSQL
while True:
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="weatherdb",
            user="weather",
            password="weatherpass",
        )
        break
    except Exception as e:
        print("⏳ Esperando a PostgreSQL...", e)
        time.sleep(3)

cursor = conn.cursor()

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"📥 Recibido: {data}")

    cursor.execute(
        """
        INSERT INTO weather_logs (station_id, temperature, humidity_percent, pressure, raw_json)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            data["station_id"],
            data["temperature"],
            data["humidity"],
            data["pressure"],
            json.dumps(data),
        ),
    )

    conn.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("💾 Guardado en PostgreSQL")

channel.basic_consume(queue="weather_data", on_message_callback=callback)
channel.start_consuming()
