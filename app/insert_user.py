from database import SessionLocal, UserDB
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

username = "user"
password = "abc123"
hashed_password = pwd_context.hash(password)

user = UserDB(username=username, hashed_password=hashed_password, disabled=False)
db.add(user)
db.commit()
db.close()
