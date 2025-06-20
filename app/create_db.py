#!/usr/bin/env python3
from database import Base, engine
from sqlalchemy import create_engine

# Ajusta esta cadena según tu configuración real de usuario, contraseña, host y base de datos
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:abc123@mysql:3306/appdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

if __name__ == "__main__":
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")
