from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    product_id = Column(String, unique=True, nullable=False)  # id de VTEX (Día)
    name = Column(String, nullable=False)
    brand = Column(String)
    category_id = Column(String)
    category_name = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    prices = relationship("PriceHistory", back_populates="product")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    list_price = Column(Numeric(10, 2))
    available_quantity = Column(Integer)
    checked_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="prices")