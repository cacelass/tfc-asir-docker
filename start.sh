#!/bin/bash
set -e

# 1. Habilitar módulos de Apache necesarios
echo ">> Habilitando módulos de Apache: proxy, proxy_http..."
docker run --rm \
  -v "$PWD/apache/httpd.conf":/usr/local/apache2/conf/httpd.conf \
  httpd:2.4 \
  bash -c " \
    sed -i 's|#LoadModule proxy_module|LoadModule proxy_module|' /usr/local/apache2/conf/httpd.conf && \
    sed -i 's|#LoadModule proxy_http_module|LoadModule proxy_http_module|' /usr/local/apache2/conf/httpd.conf \
  " || true

# 2. Ajustar /etc/hosts en el host
echo ">> Añadiendo entradas a /etc/hosts..."
HOST1="127.0.0.1 holamundo.local"
HOST2="127.0.0.1 adiosmundo.local"
grep -qF "$HOST1" /etc/hosts || echo "$HOST1" | sudo tee -a /etc/hosts
grep -qF "$HOST2" /etc/hosts || echo "$HOST2" | sudo tee -a /etc/hosts

# 3. Construir y levantar todos los contenedores
echo ">> Levantando servicios con Docker Compose..."
docker compose down -v
docker compose up --build -d

# 4. Mostrar estado
echo ">> Estado de contenedores:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

echo "¡Todo levantado! Accede a http://holamundo.local y http://adiosmundo.local"
