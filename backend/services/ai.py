import base64
import io
import httpx
import json
import re
import unicodedata
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

Reglas adicionales:
- No uses palabras genéricas como "Factura" o "Invoice" para el campo empresa
- Respeta exactamente las claves del JSON (sin tildes)

Si no puedes determinar cualquier otro campo, usa null."""

def limpiar_respuesta(respuesta_raw: str) -> str:
    limpio = re.sub(r"```(?:json)?", "", respuesta_raw).strip()
    limpio = limpio.replace("```", "").strip()
    return limpio

def _normalizar_clave(clave: str) -> str:
    clave = clave.strip().lower()
    clave = unicodedata.normalize("NFKD", clave)
    clave = "".join(ch for ch in clave if not unicodedata.combining(ch))
    clave = clave.replace(" ", "_")
    return clave

def _parse_monto(valor):
    if isinstance(valor, (int, float)):
        return float(valor)
    if not isinstance(valor, str):
        return None
    limpio = re.sub(r"[^0-9,\.]", "", valor)
    if not limpio:
        return None
    if "." in limpio and "," in limpio:
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
    elif "," in limpio:
        limpio = limpio.replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        return None

def _normalizar_fecha(valor):
    if not isinstance(valor, str):
        return valor
    valor = valor.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", valor):
        return valor
    match = re.match(r"^(\d{2})[/-](\d{2})[/-](\d{4})$", valor)
    if match:
        dia, mes, anio = match.groups()
        return f"{anio}-{mes}-{dia}"
    return valor

def normalizar_resultado(resultado: dict) -> dict:
    if not isinstance(resultado, dict):
        raise ValueError("Respuesta de LLaVA no es un objeto JSON")

    alias = {
        "numero_factura": {
            "numero_factura",
            "numero",
            "numero_de_factura",
            "no_factura",
            "num_factura",
            "n_factura",
        },
        "nombre_cliente": {
            "nombre_cliente",
            "cliente",
            "nombre_del_cliente",
            "razon_social_cliente",
        },
        "descripcion": {"descripcion", "detalle", "concepto"},
    }
    esperadas = {
        "empresa",
        "categoria",
        "monto",
        "fecha",
        "numero_factura",
        "descripcion",
        "nombre_cliente",
    }

    normalizado = {}
    for clave, valor in resultado.items():
        clave_norm = _normalizar_clave(str(clave))
        clave_final = None

        if clave_norm in esperadas:
            clave_final = clave_norm
        else:
            for destino, opciones in alias.items():
                if clave_norm in opciones:
                    clave_final = destino
                    break

        if clave_final:
            normalizado[clave_final] = valor

    empresa = normalizado.get("empresa")
    if isinstance(empresa, str):
        empresa_limpia = _normalizar_clave(empresa)
        if empresa_limpia in {"factura", "invoice"}:
            normalizado["empresa"] = None

    if "monto" in normalizado:
        monto = _parse_monto(normalizado.get("monto"))
        normalizado["monto"] = monto

    if "fecha" in normalizado:
        normalizado["fecha"] = _normalizar_fecha(normalizado.get("fecha"))

    if "descripcion" in normalizado and isinstance(normalizado["descripcion"], str):
        normalizado["descripcion"] = normalizado["descripcion"].strip()

    if "categoria" in normalizado and isinstance(normalizado["categoria"], str):
        normalizado["categoria"] = normalizado["categoria"].strip()

    if "nombre_cliente" in normalizado and isinstance(normalizado["nombre_cliente"], str):
        normalizado["nombre_cliente"] = normalizado["nombre_cliente"].strip()

    return normalizado

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
            return normalizar_resultado(resultado)
        except json.JSONDecodeError:
            raise ValueError(f"LLaVA no devolvió un JSON válido: {texto_limpio[:200]}")