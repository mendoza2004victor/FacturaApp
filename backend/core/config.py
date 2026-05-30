# Configuración central del backend
# Modifica estos valores según tu entorno

# Ollama corre localmente en este puerto por defecto
OLLAMA_URL = "http://localhost:11434/api/generate"

# Modelo que usamos - LLaVA 7B
OLLAMA_MODEL = "llava:7b"

# Timeouts por paso del pipeline (en segundos)
TIMEOUT_PREPROCESAMIENTO = 3
TIMEOUT_OCR = 8
TIMEOUT_OLLAMA = 180

# Mínimo de caracteres que debe extraer el OCR para considerarse válido
MIN_TEXTO_OCR = 20

# Base de datos SQLite
DATABASE_URL = "sqlite:///./facturapp.db"
