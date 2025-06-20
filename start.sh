#!/bin/bash
set -e

echo "Selecciona el sistema operativo:"
echo "1) Linux"
echo "2) Windows"
read -rp "Introduce 1 o 2: " SO

HOST_LINE="127.0.0.1 tfc.local"

case "$SO" in
  1)
    echo "Has seleccionado Linux."
    # Añadir dominio local a /etc/hosts (Linux)
    if ! grep -qF "$HOST_LINE" /etc/hosts; then
      echo "$HOST_LINE" >> /etc/hosts
      echo "Línea añadida a /etc/hosts"
    else
      echo "La línea ya existe en /etc/hosts"
    fi
    ;;
  2)
    echo "Has seleccionado Windows."
    echo "Por favor, ejecuta el archivo start.ps1 desde PowerShell como administrador para continuar en Windows."
    exit 0
    ;;
  *)
    echo "Opción no válida. Debes introducir 1 o 2."
    exit 1
    ;;
esac

# Apagar y limpiar contenedores y volúmenes previos
echo ">> Limpiando contenedores previos..."
docker compose down -v

# Levantar los servicios (build incluido)
echo ">> Levantando servicios con Docker Compose..."
docker compose up --build -d

# Esperar a que MySQL esté healthy según healthcheck
echo ">> Esperando a que MySQL esté completamente preparado..."
for i in {1..60}; do
  STATUS="$(docker inspect --format='{{.State.Health.Status}}' $(docker compose ps -q mysql) 2>/dev/null || echo "starting")"
  if [ "$STATUS" == "healthy" ]; then
    echo "MySQL está healthy."
    break
  fi
  echo "Esperando a que MySQL esté healthy... ($i/60) Estado actual: $STATUS"
  sleep 2
done

# Espera activa dentro del contenedor app hasta que el puerto 3306 acepte conexiones
echo ">> Esperando confirmación de acceso real a MySQL desde app..."
docker compose exec app bash -c '
for i in $(seq 1 60); do
  if mysql -h "mysql" -u"user" -p"abc123" -e "SELECT 1" "appdb" >/dev/null 2>&1; then
    exit 0
  fi
  echo "Esperando a que MySQL acepte conexiones TCP ($i/60)..."
  sleep 1
done
echo "ERROR: No se pudo acceder a MySQL desde app" >&2
exit 1
'

# Formatear scripts y permisos en app
docker compose exec app bash -c 'command -v dos2unix >/dev/null || apt-get update && apt-get install -y dos2unix'
docker compose exec app dos2unix create_db.py
docker compose exec app chmod +x create_db.py
if docker compose exec app test -f insert_user.py; then
  docker compose exec app dos2unix insert_user.py
  docker compose exec app chmod +x insert_user.py
fi

# Inicializar base de datos y usuario en el contenedor app
echo ">> Creando tablas y usuario en la base de datos..."
docker compose exec -T app ./create_db.py || (echo "ERROR: create_db.py falló" && exit 1)
if docker compose exec app test -f insert_user.py; then
  docker compose exec -T app ./insert_user.py || (echo "ERROR: insert_user.py falló" && exit 1)
fi

# Mostrar estado de los contenedores
echo ">> Estado de contenedores:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

echo "¡Todo levantado! Accede a:"
echo "  http://tfc.local"

echo "¡Para acceder a swagger acceda a:"
echo "  http://tfc.local/8000"

