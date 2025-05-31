from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

app = FastAPI()
Base = declarative_base()

# Configuración de la base de datos
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_NAME = os.getenv("DB_NAME", "loginapp")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

class LoginRequest(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Servir archivos estáticos desde la carpeta "static"
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Endpoint de login
@app.post("/login")
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(
        Usuario.username == login_req.username,
        Usuario.password == login_req.password
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"message": "Inicio de sesión exitoso"}

# Endpoint opcional (puedes quitarlo si ya no lo necesitas)
@app.get("/api")
def read_root():
    return {"message": "Hola Mundo - FastAPI con login"}
