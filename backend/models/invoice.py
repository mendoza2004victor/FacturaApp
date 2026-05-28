from pydantic import BaseModel
from typing import Optional
from datetime import date

# Estructura de una factura extraída por la IA
class InvoiceData(BaseModel):
    empresa: Optional[str] = None
    categoria: Optional[str] = None
    monto: Optional[float] = None
    fecha: Optional[str] = None

# Respuesta exitosa del endpoint /scan
class InvoiceResponse(BaseModel):
    status: str
    invoice: dict

# Estructura de una factura guardada en la base de datos
class InvoiceDB(BaseModel):
    id: str
    empresa: str
    categoria: str
    monto: float
    fecha: str
    color: str  # Color asignado dinámicamente a la categoría

    class Config:
        from_attributes = True
