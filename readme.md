# Proyecto FastAPI con Docker, SQLAlchemy y Nginx/Apache

## Introducción

Este proyecto demuestra el desarrollo de una aplicación web en Python utilizando **FastAPI** como framework principal de backend, **SQLAlchemy** para la capa ORM, y contenedores **Docker** para el despliegue. Incluye dos endpoints básicos (`/holamundo` y `/adiosmundo`) que sirven de ejemplo para exponer múltiples rutas en una sola instancia de FastAPI.

## Objetivos

* Implementar una API RESTful sencilla con FastAPI.
* Validar y serializar datos usando **Pydantic**.
* Interactuar con una base de datos **MySQL** mediante SQLAlchemy.
* Contenerizar la aplicación y servicios asociados con Docker y Docker Compose.
* Configurar un proxy inverso con **Nginx** y servir estáticos con **Apache**.

## Tecnologías

* `Python 3.9`
* `FastAPI` + `Uvicorn`
* `Pydantic`
* `SQLAlchemy`
* `MySQL 8.0`
* `Apache HTTP Server`
* `Nginx`
* `Docker` + `Docker Compose`
* `Git` para control de versiones

## Estructura del Proyecto

```text
├── app/
│   ├── main.py           # Punto de entrada FastAPI
│   ├── routers/          # Definición de endpoints organizados
│   ├── models/           # Clases ORM SQLAlchemy
│   ├── schemas/          # Modelos Pydantic
│   ├── crud/             # Operaciones CRUD
│   ├── dependencies.py   # Inyección de dependencias
│   ├── database.py       # Configuración de la base de datos
│   └── utils.py          # Funciones auxiliares
├── Dockerfile            # Construcción de imagen de la app
├── docker-compose.yml    # Orquestación de servicios
├── nginx/                # Configuración Nginx como proxy inverso
├── apache/               # Configuración Apache para estáticos
├── requirements.txt      # Dependencias Python
└── README.md             # Documentación del proyecto
```

## Instalación y Uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/proyecto-fastapi.git
cd proyecto-fastapi
```

### 2. Dar permisos y ejecutar script 

```bash
chmod +x inicio.sh
./inicio.sh
```

### 3. Acceder a la API

* Documentación interactiva Swagger: http://tfc.local:80/docs
* Endpoint ejemplo `/holamundo`: http://tfc.local/holamundo
* Endpoint ejemplo `/adiosmundo`: http://tfc.local/adiosmundo


