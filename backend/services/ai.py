import httpx
import json
import re
from core.config import OLLAMA_URL, OLLAMA_MODEL, TIMEOUT_QWEN

def construir_prompt(texto_ocr: str) -> str:
    return f"""Eres un asistente especializado en análisis de facturas en español.
Dado el siguiente texto extraído de una factura, responde ÚNICAMENTE con un JSON válido.
No agregues explicaciones, comentarios ni bloques de código.

Estructura requerida:
{{
  "empresa": "nombre de la empresa emisora de la factura",
  "categoria": "tipo de servicio en una sola palabra en español (ejemplo: Electricidad, Agua, Internet, Alquiler, Telefonia)",
  "monto": 00.00,
  "fecha": "YYYY-MM-DD",
  "numero_factura": "número o código de la factura",
  "descripcion": "descripción breve del servicio o producto",
  "nombre_cliente": "nombre completo del cliente"
}}

Reglas importantes para el monto:
- Busca cualquier número que represente el total a pagar
- Si encuentras el monto escrito en texto como "ciento cincuenta quetzales" conviértelo a número: 150.00
- Si ves símbolos como Q., Q, GTQ, $, conviértelos solo al número
- Si hay varios montos, toma el total final o el más alto
- Solo si es absolutamente imposible determinarlo, usa null

Si no puedes determinar cualquier otro campo, usa null.

Texto de la factura:
{texto_ocr[:2000]}"""

def limpiar_respuesta(respuesta_raw: str) -> str:
    limpio = re.sub(r"```(?:json)?", "", respuesta_raw).strip()
    limpio = limpio.replace("```", "").strip()
    return limpio

async def analizar_con_qwen(texto_ocr: str) -> dict:
    prompt = construir_prompt(texto_ocr)

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 250,
            "temperature": 0.1,
        }
    }

    async with httpx.AsyncClient(timeout=TIMEOUT_QWEN) as cliente:
        respuesta = await cliente.post(OLLAMA_URL, json=payload)
        respuesta.raise_for_status()

        datos = respuesta.json()
        texto_respuesta = datos.get("response", "")

        texto_limpio = limpiar_respuesta(texto_respuesta)

        try:
            resultado = json.loads(texto_limpio)
            return resultado
        except json.JSONDecodeError as e:
            raise ValueError(f"Qwen no devolvió un JSON válido: {texto_limpio[:200]}")