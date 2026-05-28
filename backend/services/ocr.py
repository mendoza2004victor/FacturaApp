import pytesseract
from PIL import Image
from core.config import MIN_TEXTO_OCR

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extraer_texto(imagen: Image.Image) -> str:
    """
    Extrae el texto de la imagen preprocesada usando Tesseract.
    Lanza ValueError si el texto extraído es insuficiente.
    """
    # Configuración para mejorar detección de texto en documentos
    config = "--oem 3 --psm 6"

    # Intenta primero en español, luego en inglés como respaldo
    try:
        texto = pytesseract.image_to_string(imagen, lang="spa", config=config)
    except Exception:
        texto = pytesseract.image_to_string(imagen, lang="eng", config=config)

    # Limpia el texto de caracteres extraños
    texto_limpio = texto.strip()

    # Verifica que haya suficiente texto para analizar
    if len(texto_limpio) < MIN_TEXTO_OCR:
        raise ValueError(f"Texto insuficiente extraído: '{texto_limpio}'")

    return texto_limpio
