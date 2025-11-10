# Imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del productor dentro del contenedor
COPY . .

# Instala las dependencias necesarias
RUN pip install pika

# Comando para ejecutar el productor
CMD ["python", "producer.py"]
