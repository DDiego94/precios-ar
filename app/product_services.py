from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Product, PriceHistory
from app.dia_client import buscar_productos, obtener_producto_por_id

def guardar_producto(sesion: Session, dato) -> Product:
    product = sesion.query(Product).filter(Product.product_id == dato["productId"]).first()
    if not product:
        item = dato["items"][0]
        product = Product(
            product_id=dato["productId"],
            name=dato["productName"],
            brand=dato.get("brand"),
            category_id=dato.get("categoryId"),
            category_name=dato["categories"][0] if dato.get("categories") else None,
            image_url=item["images"][0]["imageUrl"] if item["images"] else None,
        )
        sesion.add(product)
    return product


def registrar_precio(sesion: Session, product: Product, dato) -> None:
    item = dato["items"][0]
    oferta = item["sellers"][0]["commertialOffer"]
    sesion.add(PriceHistory(
        product_id=product.id,
        price=oferta["Price"],
        list_price=oferta.get("ListPrice"),
        available_quantity=oferta.get("AvailableQuantity"),
    ))


def sincronizar(query: str) -> int:
    datos = buscar_productos(query)
    sesion = SessionLocal()
    try:
        for dato in datos:
            product = guardar_producto(sesion, dato)
            sesion.flush()
            registrar_precio(sesion, product, dato)
        sesion.commit()
        return len(datos)
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()

def actualizar_todos() -> int:
    sesion = SessionLocal()
    try:
        productos = sesion.query(Product).all()
        actualizados = 0
        for producto in productos:
            dato = obtener_producto_por_id(producto.product_id)
            if dato:
                if dato.get("productName"):
                    producto.name = dato["productName"]
                if dato.get("brand"):
                    producto.brand = dato["brand"]
                sesion.flush()
                registrar_precio(sesion, producto, dato)
                actualizados += 1
        sesion.commit()
        return actualizados
    except Exception:
        sesion.rollback()
        raise
    finally:
        sesion.close()