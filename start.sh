#!/bin/bash
set -e

# 1. Ajustar /etc/hosts en el host
echo ">> Añadiendo entradas a /etc/hosts..."
HOST1="127.0.0.1 holamundo.local"
HOST2="127.0.0.1 adiosmundo.local"
grep -qF "$HOST1" /etc/hosts || echo "$HOST1" | tee -a /etc/hosts
grep -qF "$HOST2" /etc/hosts || echo "$HOST2" | tee -a /etc/hosts

# 2. Construir y levantar todos los contenedores
echo ">> Levantando servicios con Docker Compose..."
docker compose down -v
docker compose up --build -d

# 3. Mostrar estado
echo ">> Estado de contenedores:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

echo "¡Todo levantado! Accede a http://holamundo.local:8080/ y http://adiosmundo.local:8080/"
