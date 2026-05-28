import base64
import io
import httpx
import json
import re
from PIL import Image
from core.config import OLLAMA_URL, OLLAMA_MODEL, TIMEOUT_OLLAMA

def construir_prompt() -> str:
        return """Eres un asistente especializado en análisis de facturas en español.
Vas a recibir una imagen de una factura y debes extraer los datos.
Responde ÚNICAMENTE con un JSON válido. No agregues explicaciones ni bloques de código.

Estructura requerida:
{
    "empresa": "nombre de la empresa emisora de la factura",
    "categoria": "tipo de servicio en una sola palabra en español (ejemplo: Electricidad, Agua, Internet, Alquiler, Telefonia)",
    "monto": 00.00,
    "fecha": "YYYY-MM-DD",
    "numero_factura": "número o código de la factura",
    "descripcion": "descripción breve del servicio o producto",
    "nombre_cliente": "nombre completo del cliente"
}

Reglas importantes para el monto:
- Busca cualquier número que represente el total a pagar
- Si encuentras el monto escrito en texto como "ciento cincuenta quetzales" conviértelo a número: 150.00
- Si ves símbolos como Q., Q, GTQ, $, conviértelos solo al número
- Si hay varios montos, toma el total final o el más alto
- Solo si es absolutamente imposible determinarlo, usa null

Si no puedes determinar cualquier otro campo, usa null."""

def limpiar_respuesta(respuesta_raw: str) -> str:
    limpio = re.sub(r"```(?:json)?", "", respuesta_raw).strip()
    limpio = limpio.replace("```", "").strip()
    return limpio

async def analizar_con_llava(imagen: Image.Image) -> dict:
    prompt = construir_prompt()

    buffer = io.BytesIO()
    imagen.save(buffer, format="JPEG")
    imagen_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "images": [imagen_b64],
        "options": {
            "num_predict": 300,
            "temperature": 0.1,
        }
    }

    async with httpx.AsyncClient(timeout=TIMEOUT_OLLAMA) as cliente:
        respuesta = await cliente.post(OLLAMA_URL, json=payload)
        respuesta.raise_for_status()

        datos = respuesta.json()
        texto_respuesta = datos.get("response", "")

        texto_limpio = limpiar_respuesta(texto_respuesta)

        try:
            resultado = json.loads(texto_limpio)
            return resultado
        except json.JSONDecodeError:
            raise ValueError(f"LLaVA no devolvió un JSON válido: {texto_limpio[:200]}")