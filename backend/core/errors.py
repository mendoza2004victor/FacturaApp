from fastapi import HTTPException

# Nivel 1 — Timeout: el proceso tardó demasiado
def error_timeout():
    raise HTTPException(
        status_code=408,
        detail={
            "status": "timeout",
            "mensaje": "No fue posible analizar esta factura, el proceso tardó demasiado. Intenta de nuevo."
        }
    )

# Nivel 2 — OCR sin resultado: la imagen no tiene texto legible
def error_ocr():
    raise HTTPException(
        status_code=422,
        detail={
            "status": "ocr_failed",
            "mensaje": "La imagen no tiene suficiente calidad para ser analizada. Intenta con mejor iluminación."
        }
    )

# Nivel 3 — Qwen falló: el modelo no pudo extraer los datos
def error_ai():
    raise HTTPException(
        status_code=422,
        detail={
            "status": "analysis_failed",
            "mensaje": "No fue posible extraer los datos de esta factura. Intenta de nuevo o ingresa los datos manualmente."
        }
    )

# Error genérico para cualquier fallo inesperado
def error_generico(detalle: str = ""):
    raise HTTPException(
        status_code=500,
        detail={
            "status": "server_error",
            "mensaje": f"Error interno del servidor. {detalle}"
        }
    )
