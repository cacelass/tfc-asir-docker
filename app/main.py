#!/usr/bin/env python3
from fastapi import FastAPI, Form, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal, UserDB
import requests
from datetime import date

app = FastAPI()

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("static/index.html")

@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
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
    return JSONResponse({"autenticado": "si", "usuario": username})
@app.get("/holamundo")
def hola_mundo(
    autenticado: str = Header(""),
    usuario: str = Header(None), 
    db: Session = Depends(get_db)
):
    if autenticado != "si":
        raise HTTPException(status_code=401, detail="No autenticado")
    if usuario is None:
        raise HTTPException(status_code=400, detail="Falta el usuario en el header")
    user = db.query(UserDB).filter(UserDB.username == usuario).first()
    if not user:
        return JSONResponse({
            "usuario": usuario,
            "provincia": "Desconocida",
            "foto_perfil": "",
            "edad": "",
            "tiempo": "No disponible",
            "bienvenida": "Bienvenidos al TFC de Alejandro Cancelas"
        }, headers={"Content-Type": "application/json; charset=utf-8"})
    provincia_user = user.provincia or "Desconocida"
    foto_perfil = user.foto_perfil or ""
    edad = user.edad if user.edad is not None else ""
    tiempo_actual = "No disponible"
    nombre_provincia = provincia_user
    try:
        resp = requests.get("https://www.el-tiempo.net/api/json/v2/provincias")
        resp.encoding = 'utf-8'
        lista = resp.json()["provincias"]
        provincia_obj = next((p for p in lista if p["NOMBRE_PROVINCIA"].lower() == provincia_user.lower()), None)
        if provincia_obj:
            codprov = provincia_obj["CODPROV"]
            detalle_resp = requests.get(f"https://www.el-tiempo.net/api/json/v2/provincias/{codprov}")
            detalle_resp.encoding = 'utf-8'
            detalle = detalle_resp.json()
            tiempo_actual = detalle['today']['p']
            nombre_provincia = provincia_obj["NOMBRE_PROVINCIA"]
    except Exception:
        pass
    return JSONResponse({
        "usuario": user.username,
        "provincia": nombre_provincia,
        "foto_perfil": foto_perfil,
        "edad": edad,
        "tiempo": tiempo_actual,
        "bienvenida": "Bienvenidos al TFC de Alejandro Cancelas"
    }, headers={"Content-Type": "application/json; charset=utf-8"})

@app.get("/adiosmundo")
def adios_mundo(autenticado: str = Header("")):
    if autenticado != "si":
        raise HTTPException(status_code=401, detail="No autenticado")
    return JSONResponse({"msg": "¡Adiós mundo!"}, headers={"Content-Type": "application/json; charset=utf-8"})
