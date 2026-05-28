from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router
from api.auth_routes import router as auth_router
import traceback

app = FastAPI(
    title="FacturApp API",
    description="Backend para análisis de facturas con Qwen 2.5 y Tesseract OCR",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_errores(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        print("ERROR INTERNO:")
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")

@app.get("/")
def root():
    return {"status": "FacturApp backend corriendo correctamente"}