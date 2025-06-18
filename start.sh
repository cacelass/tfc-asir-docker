#!/bin/bash
set -e

# Añadir dominios locales a /etc/hosts si no existen
HOST1="127.0.0.1 holamundo.local"
HOST2="127.0.0.1 adiosmundo.local"
if ! grep -qF "$HOST1" /etc/hosts; then
  echo "$HOST1" >> /etc/hosts
fi
if ! grep -qF "$HOST2" /etc/hosts; then
  echo "$HOST2" >> /etc/hosts
fi

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

# Asegura formato UNIX y permisos de ejecución para scripts en el contenedor app
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
echo "  http://holamundo.local:8080/holamundo"
echo "  http://adiosmundo.local:8080/adiosmundo"
#!/bin/bash
set -e

# Añadir dominio local tfc.local a /etc/hosts si no existe
HOST="127.0.0.1 tfc.local"
if ! grep -qF "$HOST" /etc/hosts; then
  echo "$HOST" | sudo tee -a /etc/hosts
fi

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

# Asegura formato UNIX y permisos de ejecución para scripts en el contenedor app
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
echo "  http://tfc.local:8080/holamundo"
echo "  http://tfc.local:8080/adiosmundo"
