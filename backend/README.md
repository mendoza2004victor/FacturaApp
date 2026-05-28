# FacturApp — Backend

Sistema de gestión de facturas con OCR e IA usando Qwen 2.5, Tesseract y FastAPI.

## Requisitos previos
- Python 3.9+
- Tesseract OCR instalado en el sistema
- Ollama corriendo con el modelo qwen2.5:1.5b
- poppler instalado (para procesar PDFs)

## Instalación

1. Abre la terminal en la carpeta /backend

2. Instala las dependencias:
pip install -r requirements.txt

3. Instala el modelo Qwen en Ollama:
ollama pull qwen2.5:1.5b

4. Si estás en Windows, abre services/ocr.py y descomenta esta línea:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

5. Asegúrate que Ollama esté corriendo:
ollama serve

6. Arranca el backend:
uvicorn main:app --reload --host 0.0.0.0 --port 8000

## Endpoints disponibles

### Autenticación
- POST /api/auth/registro — Crea un nuevo usuario
- POST /api/auth/login   — Inicia sesión y devuelve token JWT
- GET  /api/auth/perfil  — Devuelve datos del usuario autenticado

### Facturas
- POST   /api/scan              — Escanea una factura (imagen o PDF)
- GET    /api/facturas          — Lista facturas del usuario autenticado
- DELETE /api/facturas/{id}     — Elimina una factura

### Chat IA
- POST /api/chat — Envía mensaje a FacturBot con contexto de facturas

## Estructura del proyecto
/backend
├── main.py
├── requirements.txt
├── /api
│   ├── routes.py          # Endpoints de facturas y chat
│   └── auth_routes.py     # Endpoints de autenticación
├── /core
│   ├── config.py          # Configuración global
│   ├── database.py        # Modelos SQLite con SQLAlchemy
│   ├── errors.py          # Manejo de errores
│   └── auth.py            # JWT y autenticación
├── /services
│   ├── file_handler.py    # Manejo de imágenes y PDFs
│   ├── preprocessor.py    # Preprocesamiento con OpenCV
│   ├── ocr.py             # Extracción de texto con Tesseract
│   └── ai.py              # Comunicación con Qwen via Ollama
├── /models
│   └── invoice.py         # Modelos Pydantic
└── /utils
└── validators.py      # Validación y colores dinámicos

## Pipeline de escaneo
Imagen/PDF → OpenCV → Tesseract OCR → Qwen 2.5B → Validación → SQLite

## Campos extraídos por factura
- empresa
- categoria (dinámica, inferida por Qwen)
- monto
- fecha
- numero_factura
- descripcion
- nombre_cliente
- color (asignado automáticamente por categoría)

## Manejo de errores
- Nivel 1: Timeout (proceso supera el límite de tiempo)
- Nivel 2: OCR fallido (imagen sin texto legible)
- Nivel 3: IA fallida (Qwen no pudo extraer los datos)

## Deploy en VPS

1. Instala Ollama en el servidor:
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:1.5b

2. Instala Tesseract:
sudo apt install tesseract-ocr tesseract-ocr-spa

3. Instala poppler:
sudo apt install poppler-utils

4. Instala dependencias Python:
pip install -r requirements.txt

5. Arranca el backend en producción:
uvicorn main:app --host 0.0.0.0 --port 8000

6. Actualiza la URL del backend en el frontend:
   - Abre frontend/src/services/api.js
   - Cambia BASE_URL por la IP pública del VPS

## Probar que funciona
http://tu-servidor:8000
http://tu-servidor:8000/docs

## Conexión desde el teléfono (demo local)
1. Conecta tu computadora y el teléfono a la misma red WiFi
2. Obtén la IP local: ejecuta `ipconfig` en Windows
3. Cambia BASE_URL en frontend/src/services/api.js por esa IP
const BASE_URL = 'http://192.168.1.x:8000';