import hashlib
import os
import jwt
from datetime import datetime, timedelta
from app.config import Settings

settings = Settings()


def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    hasheado = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 100_000
    ).hex()
    return f"{salt}${hasheado}"


def verificar_password(password: str, almacenado: str) -> bool:
    salt, hasheado = almacenado.split("$")
    candidato = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 100_000
    ).hex()
    return candidato == hasheado


def crear_token(username: str) -> str:
    payload = {"sub": username, "exp": datetime.now() + timedelta(hours=24)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def validar_token(token: str) -> str:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    return payload["sub"]