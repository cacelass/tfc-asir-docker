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

app.mount("/static", StaticFiles(directory="static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Diccionarios de traducción de códigos
ICONO_CEO = {
    101: "Despejado",
    103: "Nubes y claros",
    105: "Cubierto",
    107: "Chubascos",
    111: "Lluvia",
    201: "Noche sin lluvia",
    211: "Noche con lluvia",
    -9999: "Sin dato"
}
ICONO_TEMP = {
    -9999: "Sen dato",
    400: "Temperaturas en descenso",
    401: "Temperaturas sin cambios",
    402: "Temperaturas en ascenso"
}
ICONO_VENTO = {
    -9999: "Sen dato",
    301: "N débil",
    302: "NE débil",
    303: "E débil",
    304: "SE débil",
    305: "S débil",
    306: "SW débil",
    307: "W débil",
    308: "NW débil",
    309: "N moderado",
    310: "NE moderado",
    311: "E moderado",
    312: "SE moderado",
    313: "S moderado",
    314: "SW moderado",
    315: "W moderado",
    316: "NW moderado",
    317: "N fuerte",
    318: "NE fuerte",
    319: "E fuerte",
    320: "SE fuerte",
    321: "S fuerte",
    322: "SW fuerte",
    323: "W fuerte",
    324: "NW fuerte",
    300: "Viento variable"
}

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
            "bienvenida": "Bienvenidos al TFC de Alejandro Cancelas",
            "meteo": {}
        }, headers={"Content-Type": "application/json; charset=utf-8"})
    provincia_user = user.provincia or "Desconocida"
    foto_perfil = user.foto_perfil or ""
    foto_perfil = f"/static/fotos/{user.foto_perfil}" if user.foto_perfil else ""
    edad = user.edad if user.edad is not None else ""
    tiempo_actual = "No disponible"
    nombre_provincia = provincia_user
    meteo = {}
    try:
        resp = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/estadoEstacionsMeteo.action")
        resp.encoding = 'utf-8'
        datos = resp.json()
        estaciones = datos.get("list", [])

        # Búsqueda robusta: por provincia, luego por concello, luego fallback
        estacion = None
        for e in estaciones:
            if provincia_user.lower() == e.get("provincia", "").lower():
                estacion = e
                break
        if not estacion:
            for e in estaciones:
                if provincia_user.lower() == e.get("concello", "").lower():
                    estacion = e
                    break
        if not estacion and estaciones:
            estacion = estaciones[0]  # fallback

        if estacion:
            temp = estacion.get("valorTemperatura", "No disponible")
            sensacion = estacion.get("valorSensTermica", "No disponible")
            ln_icono_ceo = estacion.get("lnIconoCeo", -9999)
            ln_icono_temp = estacion.get("lnIconoTemperatura", -9999)
            ln_icono_vento = estacion.get("lnIconoVento", -9999)
            estado_cielo = ICONO_CEO.get(ln_icono_ceo, "Desconocido")
            tendencia = ICONO_TEMP.get(ln_icono_temp, "Desconocido")
            viento = ICONO_VENTO.get(ln_icono_vento, "Desconocido")
            concello = estacion.get("concello", "")
            provincia = estacion.get("provincia", provincia_user)
            fecha = estacion.get("dataLocal", "")
            tiempo_actual = f"{temp}ºC (Sensación: {sensacion}ºC), {estado_cielo}, {tendencia}, Viento: {viento} [{fecha}]"
            nombre_provincia = provincia
            meteo = {
                "temperatura": temp,
                "sensacion_termica": sensacion,
                "estado_cielo": estado_cielo,
                "estado_cielo_icono": ln_icono_ceo,
                "tendencia_temperatura": tendencia,
                "tendencia_temperatura_icono": ln_icono_temp,
                "viento": viento,
                "viento_icono": ln_icono_vento,
                "fecha": fecha,
                "concello": concello,
                "provincia": provincia
            }
    except Exception:
        pass
    return JSONResponse({
        "usuario": user.username,
        "provincia": nombre_provincia,
        "foto_perfil": foto_perfil,
        "edad": edad,
        "tiempo": tiempo_actual,
        "bienvenida": "Bienvenidos al TFC de Alejandro Cancelas",
        "meteo": meteo
    }, headers={"Content-Type": "application/json; charset=utf-8"})

@app.get("/adiosmundo")
def adios_mundo(autenticado: str = Header("")):
    if autenticado != "si":
        raise HTTPException(status_code=401, detail="No autenticado")
    return JSONResponse({"msg": "¡Adiós mundo!"}, headers={"Content-Type": "application/json; charset=utf-8"})
