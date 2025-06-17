from fastapi import HTTPException, status

def authenticate_user(username: str, password: str) -> bool:
    # Cambiar usuario y contraseña a lo solicitado
    if username == "user" and password == "abc123":
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas"
    )
