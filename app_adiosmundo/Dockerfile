# Dockerfile para app_holamundo (similar en app_adiosmundo)
FROM python:3.9

WORKDIR /app

# Instalar dependencias de Python necesarias
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy pymysql

# Copiar todo el código de la aplicación (incluyendo /static)
COPY . .

# Exponer puerto (opcionalmente, según configuración de docker-compose)
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
