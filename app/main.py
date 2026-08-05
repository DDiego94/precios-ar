import jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, PriceHistory, User
from app.product_services import sincronizar, resumen_producto
from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.security import hash_password, verificar_password, crear_token, validar_token
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler


scheduler = AsyncIOScheduler()


def job_actualizar_precios():
    actualizar_todos()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        job_actualizar_precios,
        trigger="interval",
        hours=6,
        next_run_time=datetime.now() + timedelta(minutes=1),
    )
    scheduler.start()
    print("Scheduler iniciado: actualiza precios cada 6 horas")
    yield
    scheduler.shutdown()


app = FastAPI(title="PreciosAR", lifespan=lifespan)


def get_current_user(authorization: str = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        username = validar_token(authorization.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalido")
    usuario = db.query(User).filter(User.username == username).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario


@app.get("/")
def home():
    return {"mensaje": "API de precios de supermercados argentinos"}


@app.get("/me")
def perfil(usuario: User = Depends(get_current_user)):
    return {"username": usuario.username}


@app.get("/health")
def status():
    return {"status": "ok"}


@app.get("/products")
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Product).order_by(Product.name).all()
    return [
        {"id": p.id, "product_id": p.product_id, "name": p.name,
         "brand": p.brand, "category_name": p.category_name, "image_url": p.image_url}
        for p in productos
    ]


@app.get("/products/{product_id}/history")
def historial_precios(product_id: int, db: Session = Depends(get_db)):
    producto = db.query(Product).filter(Product.id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    precios = db.query(PriceHistory).filter(PriceHistory.product_id == product_id)\
        .order_by(PriceHistory.checked_at.desc()).all()
    return {
        "producto": producto.name,
        "historial": [
            {"price": float(ph.price), "list_price": float(ph.list_price) if ph.list_price else None,
             "available_quantity": ph.available_quantity, "checked_at": ph.checked_at}
            for ph in precios
        ]
    }


@app.post("/sync")
def sincronizar_productos(query: str = "leche", usuario: User = Depends(get_current_user)):
    cantidad = sincronizar(query)
    return {"query": query, "sincronizados": cantidad}


@app.get("/products/{product_id}/resumen")
def resumen_productos(product_id: int, db: Session = Depends(get_db)):
    data = resumen_producto(db, product_id)
    if not data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return data


@app.post("/register")
def registrar(username: str, password: str, db: Session = Depends(get_db)):
    existe = db.query(User).filter(User.username == username).first()
    if existe:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    db.add(User(username=username, password_hash=hash_password(password)))
    db.commit()
    return {"mensaje": "Usuario creado"}


@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.username == username).first()
    if not usuario or not verificar_password(password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"token": crear_token(usuario.username)}