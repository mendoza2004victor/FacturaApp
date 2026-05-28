from datetime import datetime, timedelta
from jose import JWTError, jwt
import hashlib
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db, Usuario

SECRET_KEY = "facturapp_secret_key_2026"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HORAS = 24

security = HTTPBearer()

def hashear_contraseña(contraseña: str) -> str:
    return hashlib.sha256(contraseña.encode("utf-8")).hexdigest()

def verificar_contraseña(contraseña: str, hash: str) -> bool:
    return hashlib.sha256(contraseña.encode("utf-8")).hexdigest() == hash

def crear_token(usuario_id: str, nombre: str, email: str) -> str:
    datos = {
        "sub": usuario_id,
        "nombre": nombre,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HORAS)
    }
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = payload.get("sub")
        if not usuario_id:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return usuario