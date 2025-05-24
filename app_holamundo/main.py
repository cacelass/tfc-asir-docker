from fastapi import FastAPI
from .auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Hola Mundo"}
