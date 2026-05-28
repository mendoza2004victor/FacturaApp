from core.config import OLLAMA_URL, OLLAMA_MODEL
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import uuid

from core.errors import error_timeout, error_ocr, error_ai, error_generico
from core.database import get_db, Factura, init_db
from core.auth import obtener_usuario_actual
from services.file_handler import procesar_archivo
from services.preprocessor import preprocesar_imagen
from services.ocr import extraer_texto
from services.ai import analizar_con_qwen
from utils.validators import validar_invoice
import httpx
from fastapi import Request

router = APIRouter()
init_db()

@router.post("/scan")
async def escanear_factura(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    # PASO 1
    try:
        imagen = await procesar_archivo(archivo)
        print("✅ PASO 1 OK - Archivo procesado")
    except ValueError as e:
        print(f"❌ PASO 1 FALLÓ: {e}")
        error_generico(str(e))

    # PASO 2
    try:
        imagen_procesada = preprocesar_imagen(imagen)
        print("✅ PASO 2 OK - Preprocesamiento listo")
    except Exception as e:
        print(f"❌ PASO 2 FALLÓ: {e}")
        error_generico(f"Error en preprocesamiento: {str(e)}")

    # PASO 3
    try:
        texto = extraer_texto(imagen_procesada)
        print(f"✅ PASO 3 OK - Texto extraído: {texto[:100]}")
    except ValueError as e:
        print(f"❌ PASO 3 FALLÓ (OCR): {e}")
        error_ocr()
    except Exception as e:
        print(f"❌ PASO 3 FALLÓ (otro): {e}")
        error_generico(f"Error en OCR: {str(e)}")

    # PASO 4
    try:
        datos_qwen = await analizar_con_qwen(texto)
        print(f"✅ PASO 4 OK - Qwen respondió: {datos_qwen}")
    except httpx.TimeoutException:
        print("❌ PASO 4 FALLÓ: Timeout")
        error_timeout()
    except ValueError as e:
        print(f"❌ PASO 4 FALLÓ (ValueError): {e}")
        error_ai()
    except Exception as e:
        print(f"❌ PASO 4 FALLÓ (otro): {e}")
        error_ai()

    # PASO 5
    try:
        datos_validados = validar_invoice(datos_qwen)
        print(f"✅ PASO 5 OK - Validación exitosa: {datos_validados}")
    except ValueError as e:
        print(f"❌ PASO 5 FALLÓ: {e}")
        error_ai()

    # PASO 6
    try:
        factura_id = str(uuid.uuid4())
        nueva_factura = Factura(
            id=factura_id,
            usuario_id=usuario_actual.id,
            **datos_validados
        )
        db.add(nueva_factura)
        db.commit()
        db.refresh(nueva_factura)
        print("✅ PASO 6 OK - Guardado en BD")
    except Exception as e:
        print(f"❌ PASO 6 FALLÓ: {e}")
        error_generico(f"Error al guardar: {str(e)}")

    return {
        "status": "success",
        "invoice": {
            "id": nueva_factura.id,
            "empresa": nueva_factura.empresa,
            "categoria": nueva_factura.categoria,
            "monto": nueva_factura.monto,
            "fecha": nueva_factura.fecha,
            "numero_factura": nueva_factura.numero_factura,
            "descripcion": nueva_factura.descripcion,
            "nombre_cliente": nueva_factura.nombre_cliente,
            "color": nueva_factura.color
        }
    }

@router.get("/facturas")
def obtener_facturas(
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    facturas = db.query(Factura).filter(
        Factura.usuario_id == usuario_actual.id
    ).all()
    return {
        "status": "success",
        "facturas": [
            {
                "id": f.id,
                "empresa": f.empresa,
                "categoria": f.categoria,
                "monto": f.monto,
                "fecha": f.fecha,
                "numero_factura": f.numero_factura,
                "descripcion": f.descripcion,
                "nombre_cliente": f.nombre_cliente,
                "color": f.color
            }
            for f in facturas
        ]
    }

@router.delete("/facturas/{factura_id}")
def eliminar_factura(
    factura_id: str,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    factura = db.query(Factura).filter(
        Factura.id == factura_id,
        Factura.usuario_id == usuario_actual.id
    ).first()
    if not factura:
        return {"status": "error", "mensaje": "Factura no encontrada"}

    db.delete(factura)
    db.commit()
    return {"status": "success", "mensaje": "Factura eliminada correctamente"}

@router.post("/chat")
async def chat_con_ia(
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    datos = await request.json()
    mensaje = datos.get("mensaje", "").strip()

    if len(mensaje) < 3:
        return {"status": "error", "mensaje": "Mensaje muy corto"}

    # Obtiene las facturas del usuario para darle contexto a Qwen
    facturas = db.query(Factura).filter(
        Factura.usuario_id == usuario_actual.id
    ).all()

    total_gastado = sum(f.monto for f in facturas)

    # Construye resumen de facturas para el contexto
    resumen_facturas = ""
    if facturas:
        for f in facturas:
            resumen_facturas += f"- {f.empresa} | {f.categoria} | Q{f.monto} | {f.fecha}\n"
    else:
        resumen_facturas = "El usuario no tiene facturas registradas aún."

    prompt = f"""Eres FacturBot, un asistente financiero personal dentro de FacturApp.
Tu única función es ayudar al usuario a entender sus gastos y facturas registradas.

SOLO responde preguntas relacionadas con:
- Sus facturas registradas
- Sus gastos por categoría
- Su presupuesto y saldo disponible
- Comparaciones de gastos

Si el usuario pregunta algo fuera de estos temas responde exactamente:
"Solo puedo ayudarte con información sobre tus facturas y gastos en FacturApp."

Responde siempre en español, de forma breve y clara. Máximo 3 oraciones.

Datos del usuario {usuario_actual.nombre}:
Presupuesto mensual: Q1,800.00
Total gastado: Q{total_gastado:.2f}
Disponible: Q{1800 - total_gastado:.2f}

Facturas registradas:
{resumen_facturas}

Pregunta del usuario: {mensaje}"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 200,
            "temperature": 0.3,
        }
    }

    async with httpx.AsyncClient(timeout=30) as cliente:
        respuesta = await cliente.post(OLLAMA_URL, json=payload)
        datos_respuesta = respuesta.json()
        texto = datos_respuesta.get("response", "").strip()

    return {
        "status": "success",
        "respuesta": texto
    }