#!/bin/bash
HOSTS_LINE_1="127.0.0.1 holamundo.local"
HOSTS_LINE_2="127.0.0.1 adiosmundo.local"

if ! grep -q "$HOSTS_LINE_1" /etc/hosts; then
    echo "Añadiendo entradas a /etc/hosts..."
    echo "$HOSTS_LINE_1" | sudo tee -a /etc/hosts
    echo "$HOSTS_LINE_2" | sudo tee -a /etc/hosts
else
    echo "Las entradas ya existen en /etc/hosts."
fi
