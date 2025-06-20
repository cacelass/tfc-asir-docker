#!/usr/bin/env python3
from database import SessionLocal, UserDB
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cambia los valores según tus necesidades
username = "user"
password = "abc123"
provincia = "Pontevedra"
foto_perfil = "/app/static/foto_perfil.jpg"
edad = 25

db = SessionLocal()
hashed = pwd_context.hash(password)
user = UserDB(
    username=username,
    hashed_password=hashed,
    provincia=provincia,
    foto_perfil=foto_perfil,
    edad=edad
)
db.add(user)
db.commit()
db.close()
print("Usuario creado")
