from typing import Optional

PALETA_COLORES = [
    "#2563EB",
    "#EAB308",
    "#8B5CF6",
    "#60A5FA",
    "#A855F7",
    "#10B981",
    "#F59E0B",
    "#EF4444",
    "#06B6D4",
    "#84CC16",
]

colores_asignados = {}
contador_color = 0

def obtener_color_categoria(categoria: str) -> str:
    global contador_color
    categoria_normalizada = categoria.lower().strip()
    if categoria_normalizada not in colores_asignados:
        indice = contador_color % len(PALETA_COLORES)
        colores_asignados[categoria_normalizada] = PALETA_COLORES[indice]
        contador_color += 1
    return colores_asignados[categoria_normalizada]

def validar_invoice(datos: dict) -> dict:
    empresa = datos.get("empresa") or "Empresa desconocida"
    categoria = datos.get("categoria") or "General"
    monto = datos.get("monto")
    fecha = datos.get("fecha") or "2026-01-01"
    numero_factura = datos.get("numero_factura") or "Sin número"
    descripcion = datos.get("descripcion") or "Sin descripción"
    nombre_cliente = datos.get("nombre_cliente") or "Sin nombre"

    # Si el monto es null lo guardamos como 0.0
    # El frontend mostrará una alerta para que el usuario lo corrija
    if monto is None:
        monto = 0.0
    else:
        try:
            monto = float(monto)
        except (TypeError, ValueError):
            monto = 0.0

    return {
        "empresa": str(empresa),
        "categoria": str(categoria),
        "monto": monto,
        "fecha": str(fecha),
        "numero_factura": str(numero_factura),
        "descripcion": str(descripcion),
        "nombre_cliente": str(nombre_cliente),
        "color": obtener_color_categoria(str(categoria))
    }