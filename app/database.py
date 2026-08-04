from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import Settings
import time

settings = Settings()


def create_engine_with_retry():
    retires = 5
    while retires > 0:
        try:
            engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
            engine.connect()
            return engine
        except Exception:
            retires -= 1
            time.sleep(2)
    raise Exception("No se pudo conectar a la base de datos")


engine = create_engine_with_retry()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()