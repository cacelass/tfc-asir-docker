from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import HTMLResponse

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Usuario y password (hasheada)
fake_users_db = {
    "user": {
        "username": "user",
        "hashed_password": pwd_context.hash("abc123"),
        "disabled": False,
    }
}

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = get_user(fake_users_db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user.username, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = get_user(fake_users_db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")
    return user

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
      <head><title>Inicio</title></head>
      <body>
        <h1>Bienvenido a la API</h1>
        <p>Usa <a href='/docs'>/docs</a> para ver la documentación interactiva.</p>
      </body>
    </html>
    """
@app.get("/holamundo")
async def hola_mundo(current_user: User = Depends(get_current_user)):
    return {"mensaje": "¡Hola Mundo!", "user": current_user.username}

@app.get("/adiosmundo")
async def adios_mundo(current_user: User = Depends(get_current_user)):
    return {"mensaje": "¡Adiós Mundo!", "user": current_user.username}
