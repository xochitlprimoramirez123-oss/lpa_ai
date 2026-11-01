from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Si usamos SQLite local, necesitamos habilitar el uso multihilo para FastAPI
connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

# Motor principal de conexión a la base de datos
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Cambiar a True si deseas ver en consola cada consulta SQL generada
)

# Fábrica de sesiones transaccionales
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base declarativa de SQLAlchemy 2.0+ para todos los modelos ORM."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Generador de inyección de dependencias para FastAPI.
    Abre una sesión por petición HTTP y garantiza su cierre al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()