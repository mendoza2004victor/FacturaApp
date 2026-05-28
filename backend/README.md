# FacturApp — Backend

Sistema de gestión de facturas con IA usando LLaVA (Ollama) y FastAPI.

## Requisitos previos
- Python 3.9+
- Ollama instalado y corriendo con el modelo llava:7b
- poppler instalado (para procesar PDFs)

## Instalación

1. Abre la terminal en la carpeta /backend

2. Instala las dependencias:
pip install -r requirements.txt

3. Instala el modelo LLaVA en Ollama:
ollama pull llava:7b

4. Asegúrate que Ollama esté corriendo:
ollama serve

5. Arranca el backend:
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
Imagen/PDF → OpenCV → LLaVA 7B (Ollama) → Validación → SQLite

## Campos extraídos por factura
- empresa
- categoria (dinámica, inferida por LLaVA)
- monto
- fecha
- numero_factura
- descripcion
- nombre_cliente
- color (asignado automáticamente por categoría)

## Manejo de errores
- Nivel 1: Timeout (proceso supera el límite de tiempo)
- Nivel 2: IA fallida (LLaVA no pudo extraer los datos)

## Deploy en VPS (Ubuntu Server)

1. Actualiza paquetes e instala dependencias del sistema:
sudo apt update
sudo apt install -y python3 python3-venv python3-pip poppler-utils

2. Instala Ollama y el modelo LLaVA:
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llava:7b

3. Entra a la carpeta del proyecto y crea un entorno virtual:
cd /ruta/al/proyecto/backend
python3 -m venv .venv
source .venv/bin/activate

4. Instala dependencias Python:
pip install -r requirements.txt

5. Asegúrate de que Ollama esté corriendo:
ollama serve

6. Arranca el backend en producción:
uvicorn main:app --host 0.0.0.0 --port 8000

7. Actualiza la URL del backend en el frontend:
   - Abre frontend/src/services/api.js
   - Cambia BASE_URL por la IP pública del VPS y el puerto 8000
   Ejemplo: http://167.86.73.53:8000

## Deploy en VPS con systemd (recomendado)

1. Crea el servicio:
sudo nano /etc/systemd/system/facturapp.service

2. Pega este contenido (ajusta rutas reales del proyecto):

[Unit]
Description=FacturApp Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/ruta/al/proyecto/backend
Environment="PATH=/ruta/al/proyecto/backend/.venv/bin"
ExecStart=/ruta/al/proyecto/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

3. Recarga systemd y habilita el servicio:
sudo systemctl daemon-reload
sudo systemctl enable facturapp
sudo systemctl start facturapp

4. Verifica el estado:
sudo systemctl status facturapp

## Nginx como reverse proxy (HTTP)

1. Instala Nginx:
sudo apt install -y nginx

2. Crea el archivo de configuracion:
sudo nano /etc/nginx/sites-available/facturapp

3. Pega esta configuracion (solo HTTP):

server {
  listen 80;
  server_name 167.86.73.53;

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}

4. Habilita el sitio y reinicia Nginx:
sudo ln -s /etc/nginx/sites-available/facturapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

5. Cambia la URL del backend en el frontend:
   - Si usas Nginx, apunta a http://167.86.73.53
   - Si no usas Nginx, apunta a http://167.86.73.53:8000

## HTTPS (cuando tengas dominio)

1. Apunta tu dominio al VPS (registro A a 167.86.73.53)
2. Instala Certbot:
sudo apt install -y certbot python3-certbot-nginx
3. Emite el certificado:
sudo certbot --nginx -d tu-dominio.com
4. Desde el frontend usa:
https://tu-dominio.com

## Probar que funciona
http://tu-servidor:8000
http://tu-servidor:8000/docs

## Conexión desde el teléfono (demo local)
1. Conecta tu computadora y el teléfono a la misma red WiFi
2. Obtén la IP local: ejecuta `ipconfig` en Windows
3. Cambia BASE_URL en frontend/src/services/api.js por esa IP
const BASE_URL = 'http://192.168.1.x:8000';