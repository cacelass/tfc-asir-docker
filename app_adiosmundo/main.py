from .main import SessionLocal, Usuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
nuevo_usuario = Usuario(
    username="admin",
    password=pwd_context.hash("admin")
)
db.add(nuevo_usuario)
db.commit()
db.close()
