# PreciosAR

API que monitorea precios de supermercados argentinos. Consulta la API pública
de Día (VTEX), guarda el historial de precios en PostgreSQL y expone la
información por endpoints REST con autenticación JWT.

## Stack

- **Python 3.13** + **FastAPI**
- **PostgreSQL 16** (Docker) + **SQLAlchemy 2.0**
- **APScheduler**: actualización automática de precios cada 6 horas
- **JWT** con hashing de contraseñas (PBKDF2 + salt)
- **pytest** + **GitHub Actions** (CI: 4 tests en cada push)

## Requisitos

- Docker (Postgres 16)
- Python 3.13

## Instalación y uso

```bash
# 1. clonar e instalar dependencias
git clone https://github.com/DDiego94/precios-ar.git
cd precios-ar
python -m venv venv
venv/Scripts/activate           # Windows
pip install -r requirements.txt

# 2. base de datos (Postgres en Docker)
docker compose up -d db

# 3. configurar variables (crear .env)
#    DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/preciosar
#    SECRET_KEY=tu_clave_generada

# 4. crear tablas y levantar la API
python -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine)"
uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000` (docs interactivos en `/docs`).

## Endpoints

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/` | Mensaje de bienvenida | No |
| GET | `/health` | Estado del servicio | No |
| GET | `/products` | Lista productos monitoreados | No |
| GET | `/products/{id}/history` | Historial de precios de un producto | No |
| GET | `/products/{id}/resumen` | Último precio y variación (window functions) | No |
| POST | `/register` | Crear usuario | No |
| POST | `/login` | Obtener token JWT | No |
| GET | `/me` | Datos del usuario autenticado | Sí |
| POST | `/sync` | Sincronizar productos desde Día | Sí |

## Automatización

- El **scheduler** actualiza los precios de los productos guardados cada 6 horas.
- El **CI** (GitHub Actions) corre los tests en cada push: Postgres en la nube,
  `pytest`, todo verificado.
