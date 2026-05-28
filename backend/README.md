# FacturApp — Backend

## Requisitos previos
- Python 3.9+
- Tesseract OCR instalado en el sistema
- Ollama corriendo con el modelo qwen2.5:1.5b

## Instalación

1. Abre la terminal en la carpeta /backend

2. Instala las dependencias:
```
pip install -r requirements.txt
```

3. Si estás en Windows, abre services/ocr.py y descomenta esta línea ajustando la ruta:
```
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

4. Asegúrate que Ollama esté corriendo:
```
ollama serve
```

5. Arranca el backend:
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints disponibles

- POST /api/scan        — Escanea una factura (imagen o PDF)
- GET  /api/facturas    — Lista todas las facturas guardadas
- DELETE /api/facturas/{id} — Elimina una factura

## Probar que funciona

Abre en tu navegador:
```
http://localhost:8000
```

Deberías ver:
```json
{"status": "FacturApp backend corriendo correctamente"}
```

## Documentación automática

FastAPI genera documentación interactiva en:
```
http://localhost:8000/docs
```

Desde ahí puedes probar el endpoint /scan subiendo una factura directamente.

## Conexión desde el teléfono (para la demo)

1. Conecta tu computadora y el teléfono a la misma red WiFi
2. Obtén la IP de tu computadora:
   - Windows: ejecuta `ipconfig` y busca "Dirección IPv4"
3. En el frontend, usa esa IP en lugar de localhost:
   - Ejemplo: http://192.168.1.5:8000
