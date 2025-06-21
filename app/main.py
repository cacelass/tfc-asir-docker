#!/usr/bin/env python3
from fastapi import FastAPI, Form, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
# --- START: Cambios en imports para reintentos de DB y text ---
from sqlalchemy.exc import OperationalError
from sqlalchemy import text # <--- ¡Nueva importación necesaria!
import time
# --- END: Cambios en imports para reintentos de DB y text ---

from passlib.context import CryptContext
from database import SessionLocal, UserDB, engine # Asegúrate de que engine también se importa
import requests
from datetime import date
import unicodedata

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- START: Función get_db modificada con reintentos y text() ---
def get_db():
    db = None
    retries = 5 # Número de intentos
    delay = 3   # Segundos de espera entre intentos

    for i in range(retries):
        try:
            db = SessionLocal() # Intenta crear la sesión
            # Esto fuerza una conexión real al pool y verifica si el servidor MySQL está respondiendo
            db.execute(text("SELECT 1")) # <--- ¡Corrección aplicada aquí!
            print(f"DEBUG: Conexión a la base de datos establecida en intento {i+1}.")
            yield db
            break # Si la conexión fue exitosa y se rindió, sal del bucle
        except OperationalError as e:
            print(f"ERROR: No se pudo conectar a la base de datos (intento {i+1}/{retries}): {e}")
            if i < retries - 1:
                time.sleep(delay)
            else:
                # Si es el último intento y falla, levanta la excepción
                print("ERROR: Fallo definitivo al conectar a la base de datos después de varios reintentos.")
                raise HTTPException(status_code=503, detail="Servicio de base de datos no disponible.")
        except Exception as e:
            # Captura cualquier otra excepción inesperada durante la conexión
            print(f"ERROR: Error inesperado al obtener la sesión de la base de datos: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor al conectar a la base de datos.")
        finally:
            if db:
                db.close() # Asegúrate de cerrar la sesión, incluso si hubo un error antes del yield
# --- END: Función get_db modificada con reintentos y text() ---

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

def normaliza(cad):
    if not cad:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', cad)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()

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
    db: Session = Depends(get_db) # Aquí usa la función get_db con reintentos
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
            "concello": "",
            "foto_perfil": "",
            "edad": "",
            "tiempo": "No disponible",
            "bienvenida": "Bienvenidos al TFC de Alejandro Cancelas",
            "meteo": {}
        }, headers={"Content-Type": "application/json; charset=utf-8"})

    provincia_user = user.provincia or "Desconocida"
    foto_perfil = user.foto_perfil or ""
    # Construye la URL de la foto de perfil. Si user.foto_perfil es una cadena vacía, foto_perfil también lo será.
    foto_perfil = f"/static/fotos/{user.foto_perfil}" if user.foto_perfil else ""

    edad = user.edad if user.edad is not None else ""
    tiempo_actual = "No disponible" # Valor por defecto si no se puede obtener la meteo
    nombre_provincia = provincia_user
    meteo = {}

    try:
        # --- DEBUG: Comprobar la respuesta de Meteogalicia API ---
        print("\n--- Iniciando petición a Meteogalicia ---")
        resp = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/estadoEstacionsMeteo.action")
        print(f"Estado de la respuesta de Meteogalicia: {resp.status_code}")
        resp.encoding = 'utf-8' # Asegurarse de que la codificación sea correcta
        datos = resp.json()
        print(f"JSON recibido de Meteogalicia: {datos}") # Descomenta si quieres ver todo el JSON de Meteogalicia
        print("--- Fin de petición a Meteogalicia ---")
        # ---------------------------------------------------------

        estaciones = datos.get("listEstadoActual", [])
        print(f"Número de estaciones recibidas de Meteogalicia: {len(estaciones)}")

        estacion = None
        user_concello_norm = normaliza(user.concello)
        provincia_user_norm = normaliza(provincia_user)

        print(f"Usuario -> Concello normalizado: '{user_concello_norm}', Provincia normalizada: '{provincia_user_norm}'")

        # 1. Busca por concello exacto, normalizado
        for e in estaciones:
            if user_concello_norm and user_concello_norm == normaliza(e.get("concello", "")):
                estacion = e
                print(f"Estación encontrada por concello: {estacion.get('concello')}")
                break
        # 2. Si no hay, busca por provincia normalizada (solo si no se encontró por concello)
        if not estacion:
            for e in estaciones:
                if provincia_user_norm and provincia_user_norm == normaliza(e.get("provincia", "")):
                    estacion = e
                    print(f"Estación encontrada por provincia: {estacion.get('provincia')}")
                    break
        # 3. Si no hay ninguna, coge la primera disponible (si hay alguna)
        if not estacion and estaciones:
            estacion = estaciones[0]
            print(f"Ninguna estación específica, tomando la primera: {estacion.get('concello', 'N/A')}")


        if estacion:
            # --- DEBUG: Datos de la estación encontrada ---
            print(f"Datos de la estación final seleccionada (resumen): Concello={estacion.get('concello')}, Temperatura={estacion.get('valorTemperatura')}")
            # ---------------------------------------------
            temp = estacion.get("valorTemperatura", "No disponible")
            sensacion = estacion.get("valorSensTermica", "No disponible")
            ln_icono_ceo = estacion.get("lnIconoCeo", -9999)
            ln_icono_temp = estacion.get("lnIconoTemperatura", -9999)
            ln_icono_vento = estacion.get("lnIconoVento", -9999)

            estado_cielo = ICONO_CEO.get(ln_icono_ceo, "Desconocido")
            tendencia = ICONO_TEMP.get(ln_icono_temp, "Desconocido")
            viento = ICONO_VENTO.get(ln_icono_vento, "Desconocido")

            concello_meteo = estacion.get("concello", "") # Concello de la estación meteo
            provincia_meteo = estacion.get("provincia", provincia_user) # Provincia de la estación meteo
            fecha = estacion.get("dataLocal", "")

            tiempo_actual = f"{temp}ºC (Sensación: {sensacion}ºC), {estado_cielo}, {tendencia}, Viento: {viento} [{fecha}]"
            nombre_provincia = provincia_meteo # Actualizar con la provincia de la estación meteo

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
                "concello": concello_meteo,
                "provincia": provincia_meteo
            }
        else:
            print("AVISO: No se pudo encontrar una estación meteorológica para el usuario o su provincia.")

    except requests.exceptions.RequestException as e:
        print(f"ERROR: No se pudo conectar a la API de Meteogalicia: {e}")
    except ValueError as e:
        # Esto ocurre si resp.json() falla porque la respuesta no es un JSON válido
        print(f"ERROR: Error al parsear JSON de Meteogalicia: {e}. Contenido de la respuesta (si disponible): {resp.text if 'resp' in locals() else 'No disponible'}")
    except Exception as e:
        print(f"ERROR inesperado al procesar Meteogalicia: {e}")

    return JSONResponse({
        "usuario": user.username,
        "provincia": nombre_provincia,
        "concello": user.concello, # Devuelve el concello del usuario, no el de la estación meteo
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
