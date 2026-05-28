from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.database import get_db, Usuario
from core.auth import hashear_contraseña, verificar_contraseña, crear_token, obtener_usuario_actual
import uuid

router = APIRouter()

class RegistroRequest(BaseModel):
    nombre: str
    email: str
    contraseña: str

class LoginRequest(BaseModel):
    email: str
    contraseña: str

@router.post("/registro")
def registro(datos: RegistroRequest, db: Session = Depends(get_db)):
    # Verifica que el email no exista
    existe = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_usuario = Usuario(
        id=str(uuid.uuid4()),
        nombre=datos.nombre,
        email=datos.email,
        contraseña=hashear_contraseña(datos.contraseña)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    token = crear_token(nuevo_usuario.id, nuevo_usuario.nombre, nuevo_usuario.email)

    return {
        "status": "success",
        "token": token,
        "usuario": {
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email
        }
    }

@router.post("/login")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()

    if not usuario or not verificar_contraseña(datos.contraseña, usuario.contraseña):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = crear_token(usuario.id, usuario.nombre, usuario.email)

    return {
        "status": "success",
        "token": token,
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email
        }
    }

@router.get("/perfil")
def perfil(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return {
        "status": "success",
        "usuario": {
            "id": usuario_actual.id,
            "nombre": usuario_actual.nombre,
            "email": usuario_actual.email
        }
    }