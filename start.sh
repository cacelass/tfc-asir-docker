
#!/bin/bash
set -e

# 1. Añadir dominios locales a /etc/hosts (puede requerir sudo)
echo ">> Añadiendo entradas a /etc/hosts..."
HOST1="127.0.0.1 holamundo.local"
HOST2="127.0.0.1 adiosmundo.local"
grep -qF "$HOST1" /etc/hosts || echo "$HOST1" | sudo tee -a /etc/hosts
grep -qF "$HOST2" /etc/hosts || echo "$HOST2" | sudo tee -a /etc/hosts

# 2. Construir y levantar todos los contenedores
echo ">> Levantando servicios con Docker Compose..."
docker compose down -v
docker compose up --build -d

# 3. Esperar a que MySQL esté listo dentro del contenedor (oculta warning de password)
echo ">> Esperando a que MySQL esté disponible en el contenedor..."
docker compose exec -T mysql bash -c 'for i in {1..30}; do mysqladmin ping -u"user" -p"abc123" --silent 2>/dev/null && break; sleep 2; done'

# 4. Inicializar tablas y usuario (dentro del contenedor app)
echo ">> Inicializando base de datos y usuario en el contenedor app..."
docker compose exec -T app python create_db.py
docker compose exec -T app python insert_user.py

# 5. Mostrar estado
echo ">> Estado de contenedores:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

echo "¡Todo levantado! Accede a:"
echo "  http://holamundo.local:8080/holamundo"
echo "  http://adiosmundo.local:8080/adiosmundo"
