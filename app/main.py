#!/usr/bin/env python3
from fastapi import FastAPI, Form, Depends, Header, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal, UserDB

app = FastAPI()

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Contexto de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Página principal (frontend)
@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("app/static/index.html")

# Login real usando la base de datos
@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return {"message": "Login correcto"}

# Endpoints protegidos
@app.get("/holamundo")
def hola_mundo(autenticado: str = Header("")):
    if autenticado != "si":
        raise HTTPException(status_code=401, detail="No autenticado")
    return {"mensaje": "¡Hola, mundo!"}

@app.get("/adiosmundo")
def adios_mundo(autenticado: str = Header("")):
    if autenticado != "si":
        raise HTTPException(status_code=401, detail="No autenticado")
    return {"mensaje": "¡Adiós, mundo!"}
