#!/usr/bin/env python3
from fastapi import FastAPI, Form, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal, UserDB

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_from_db(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_from_db(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def require_login(request: Request):
    autenticado = request.cookies.get("autenticado")
    return autenticado == "si"

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
      <head><title>Inicio</title></head>
      <body>
        <h1>Bienvenido a la API</h1>
        <p>Usa <a href='/login'>/login</a> para iniciar sesión.</p>
        <p>O entra a <a href='/holamundo'>/holamundo</a> o <a href='/adiosmundo'>/adiosmundo</a> (requiere login).</p>
      </body>
    </html>
    """

@app.get("/login", response_class=HTMLResponse)
async def login_form():
    return """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Login</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>Login</h1>
            <form method="post" action="/login">
                <input type="text" name="username" placeholder="Usuario" required><br><br>
                <input type="password" name="password" placeholder="Contraseña" required><br><br>
                <button type="submit">Entrar</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/login", response_class=HTMLResponse)
async def login_post(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        return HTMLResponse(
            """
            <html>
                <body>
                    <h1>Login</h1>
                    <p style="color:red;">Usuario o contraseña incorrectos.</p>
                    <a href="/login">Volver</a>
                </body>
            </html>
            """, status_code=401
        )
    response = RedirectResponse(url="/holamundo", status_code=303)
    response.set_cookie(key="autenticado", value="si", max_age=1800, path="/")
    return response

@app.get("/holamundo", response_class=HTMLResponse)
async def holamundo(request: Request):
    if not require_login(request):
        html = """
        <script>
        window.location.href = "/login";
        </script>
        """
        return HTMLResponse(content=html)
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Hola Mundo</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>Bienvenidos al TFC de Alejandro Cancelas Chapela</h1>
            <p>Curso 2024-2026</p>
            <a href="/adiosmundo">Ir a despedida</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/adiosmundo", response_class=HTMLResponse)
async def adiosmundo(request: Request):
    if not require_login(request):
        html = """
        <script>
        window.location.href = "/login";
        </script>
        """
        return HTMLResponse(content=html)
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Adiós Mundo</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>Gracias por atender</h1>
            <p>¿Alguna duda?</p>
            <a href="/holamundo">Volver a bienvenida</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
