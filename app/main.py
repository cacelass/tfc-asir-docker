#!/usr/bin/env python3
from fastapi import FastAPI, Form, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal, UserDB

app = FastAPI()

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    return FileResponse("static/index.html")

# Login usando JSON desde frontend moderno
@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    # Permitir tanto JSON como formulario
    if request.headers.get("content-type", "").startswith("application/json"):
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return JSONResponse({"autenticado": "no"})
    # El frontend espera autenticado: si y el usuario
    return JSONResponse({"autenticado": "si", "usuario": username})

# Endpoints protegidos, devuelven texto plano para el frontend
@app.get("/holamundo")
def hola_mundo(autenticado: str = Header("")):
    if autenticado != "si":
        raise HTTPException(status_code=401, detail="No autenticado")
    return PlainTextResponse("¡Hola mundo!")

@app.get("/adiosmundo")
def adios_mundo(autenticado: str = Header("")):
    if autenticado != "si":
        raise HTTPException(status_code=401, detail="No autenticado")
    return PlainTextResponse("¡Adiós mundo!")
