import io
from PIL import Image
from pdf2image import convert_from_bytes
from fastapi import UploadFile

# Tipos de archivo soportados
TIPOS_IMAGEN = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
TIPOS_PDF = ["application/pdf"]

async def procesar_archivo(archivo: UploadFile) -> Image.Image:
    """
    Recibe el archivo del frontend (PDF o imagen)
    y siempre devuelve una imagen PIL lista para preprocesar.
    El resto del pipeline no necesita saber si era PDF o imagen.
    """
    contenido = await archivo.read()
    content_type = archivo.content_type

    # Si es imagen, la abre directamente
    if content_type in TIPOS_IMAGEN:
        imagen = Image.open(io.BytesIO(contenido))
        return imagen.convert("RGB")

    # Si es PDF, convierte solo la primera página a imagen
    elif content_type in TIPOS_PDF:
        paginas = convert_from_bytes(contenido, first_page=1, last_page=1, dpi=200)
        if not paginas:
            raise ValueError("El PDF no contiene páginas legibles")
        return paginas[0].convert("RGB")

    else:
        raise ValueError(f"Tipo de archivo no soportado: {content_type}. Solo se aceptan imágenes y PDFs.")
