Perfecto 💪 Aquí tienes el contenido **listo para copiar y pegar** directamente en el editor de GitHub cuando hagas clic en **“Add a README”**.

Cópialo todo tal cual👇

---

````markdown
# 🌦️ Sistema de Gestión de Logs — Estaciones Meteorológicas

## 🧑‍💻 Integrantes del Grupo
- **Diego Salcedo** — T00077067  
- **Daniel Tache** — T00069214  
- **Julio Martínez** — T00077681  
- **Andrés Ahumada** — T00077107  

---

## 📘 Descripción del Proyecto
Este proyecto implementa un **sistema de gestión de logs** para estaciones meteorológicas, utilizando una arquitectura basada en **mensajería asíncrona** con RabbitMQ, microservicios en **Python**, y una base de datos **PostgreSQL** para persistencia de datos.  

El sistema simula la recepción de datos de estaciones meteorológicas, los publica en una cola de mensajes, los procesa mediante un consumidor y los almacena de forma segura para su posterior análisis.

---

## 🧩 Componentes Principales

### 1️⃣ Productores de Datos (Producers)
- Servicio en **Python** que simula o recibe datos meteorológicos en formato **JSON**.
- Publica los mensajes en un **exchange** de RabbitMQ con mensajes **durables** (persistentes).
- Incluye manejo de errores y logs de envío.

### 2️⃣ Broker de Mensajería — RabbitMQ
- Configurado con colas **durables** y **bindings** adecuados.
- Utiliza **mensajes persistentes** para evitar pérdida de datos.
- Incluye acceso al **dashboard de administración** de RabbitMQ.
- Manejo de `prefetch_count=1` para garantizar procesamiento ordenado.

### 3️⃣ Consumidores (Consumers)
- Microservicio en **Python** que recibe los mensajes de RabbitMQ.
- Procesa cada mensaje con **acknowledgment manual** (`ack`).
- Valida los valores recibidos (temperatura, humedad, etc.) según rangos esperados.
- Persiste los datos válidos en la tabla **weather_logs** de **PostgreSQL**.
- Registra eventos y errores en logs locales.

### 4️⃣ Base de Datos — PostgreSQL
- Define un esquema de tabla `weather_logs` con columnas para:
  - id (PK)
  - estación
  - temperatura
  - humedad
  - velocidad del viento
  - fecha y hora del registro
- Conexión segura con reconexiones automáticas.
- Persistencia de datos mediante volúmenes Docker.

### 5️⃣ Docker y Orquestación
- Contenedores individuales para:
  - `producer` (Python)
  - `consumer` (Python)
  - `rabbitmq` (mensajería)
  - `postgres` (base de datos)
- Archivo **docker-compose.yml** que:
  - Garantiza arranque ordenado.
  - Define volúmenes persistentes.
  - Configura reinicio automático de contenedores.

### 6️⃣ Logs y Monitoreo
- Cada componente genera logs propios (eventos, errores, métricas).
- Se propone la futura integración con **Prometheus** y **Grafana** para monitoreo de rendimiento y visualización de datos en tiempo real.

---

## ⚙️ Requisitos Técnicos
- **Python 3.13+**
- **Librerías:** `pika`, `psycopg2`, `json`, `logging`, `time`, `os`
- **Docker** y **docker-compose**
- **RabbitMQ** y **PostgreSQL**
- **Mensajes marcados como** `persistent`
- **Procesamiento ordenado** con `prefetch_count=1`
- **Buenas prácticas** de documentación y manejo de excepciones

---

## 🚀 Ejecución del Proyecto

1️⃣ **Clonar el repositorio:**
```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
````

2️⃣ **Construir e iniciar los servicios:**

```bash
docker-compose up --build
```

3️⃣ **Verificar contenedores activos:**

```bash
docker ps
```

4️⃣ **Acceder a los servicios:**

* RabbitMQ Dashboard → [http://localhost:15672](http://localhost:15672)
  Usuario: `guest` | Contraseña: `guest`
* PostgreSQL → `localhost:5432`
  Base de datos: `weather_db`

---

## 🔍 Posibles Extensiones Futuras

* **Alertas en tiempo real:** si una variable supera umbrales definidos.
* **API REST:** para consultar logs históricos y generar reportes.
* **Integración con Grafana:** paneles en tiempo real de datos meteorológicos.
* **Escalabilidad horizontal:** múltiples consumidores en paralelo según carga.

---

## 🧠 Conclusión

Este sistema demuestra una **arquitectura de mensajería distribuida** confiable, escalable y segura, aplicable a sistemas IoT o de monitoreo ambiental. La implementación con RabbitMQ, Python y PostgreSQL permite asegurar la **integridad y persistencia de los datos meteorológicos**, incluso ante fallos o reinicios del sistema.

---

## 📄 Licencia

Proyecto académico desarrollado con fines educativos.




