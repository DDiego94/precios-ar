import httpx
from app.config import Settings

settings = Settings()

DIA_URL = "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search"


def buscar_productos(query, limite=4):
    params = {"query": query, "_from": 0, "_to": limite - 1}
    with httpx.Client(timeout=15) as client:
        respuesta = client.get(DIA_URL, params=params)
        respuesta.raise_for_status()
        return respuesta.json()