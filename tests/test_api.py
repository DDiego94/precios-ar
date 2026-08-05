from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    respuesta = client.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_products():
    respuesta = client.get("/products")
    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)


def test_history_producto_inexistente():
    respuesta = client.get("/products/999999/history")
    assert respuesta.status_code == 404


def test_sync_sin_token():
    respuesta = client.post("/sync")
    assert respuesta.status_code == 401
