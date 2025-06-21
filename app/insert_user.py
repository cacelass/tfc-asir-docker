#!/usr/bin/env python3
from database import SessionLocal, UserDB
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

usuarios = [
    {
        "username": "alejandro",
        "password": "abc123",
        "provincia": "PONTEVEDRA",
        "concello": "Vigo",
        "foto_perfil": "foto_perfil.jpg",
        "edad": 25
    },
    {
        "username": "manuel",
        "password": "abc123",
        "provincia": "PONTEVEDRA",
        "concello": "Poio",
        "foto_perfil": "foto_perfil.jpg",
        "edad": 25
    },
    {
        "username": "user",
        "password": "abc123",
        "provincia": "PONTEVEDRA",
        "concello": "Tui",
        "foto_perfil": "foto_perfil.jpg",
        "edad": 25
    }
]

db = SessionLocal()
for u in usuarios:
    hashed = pwd_context.hash(u["password"])
    user = UserDB(
        username=u["username"],
        hashed_password=hashed,
        provincia=u["provincia"],
        concello=u["concello"],
        foto_perfil=u["foto_perfil"],
        edad=u["edad"]
    )
    db.add(user)
db.commit()
db.close()
print(f"{len(usuarios)} usuarios creados")
