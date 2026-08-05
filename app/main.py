from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, PriceHistory
from app.product_services import sincronizar


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
def sincronizar_productos(query: str = "leche"):
    cantidad = sincronizar(query)
    return {"query": query, "sincronizados": cantidad}