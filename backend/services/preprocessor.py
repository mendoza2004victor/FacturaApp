import cv2
import numpy as np
from PIL import Image

def preprocesar_imagen(imagen_pil: Image.Image) -> Image.Image:
    imagen_cv = np.array(imagen_pil)

    # Escala de grises
    gris = cv2.cvtColor(imagen_cv, cv2.COLOR_RGB2GRAY)

    # Escala la imagen al doble para que Tesseract lea mejor
    escalada = cv2.resize(gris, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Umbralización de Otsu, mejor para fondos irregulares
    _, umbral = cv2.threshold(escalada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return Image.fromarray(umbral)