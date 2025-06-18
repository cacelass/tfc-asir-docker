from database import SessionLocal, UserDB
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
hashed = pwd_context.hash("abc123")
user = UserDB(username="user", hashed_password=hashed)
db.add(user)
db.commit()
db.close()
print("Usuario creado")
