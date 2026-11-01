from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Calculamos la ruta raíz del proyecto de forma dinámica para que funcione en Windows y Linux/Docker
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Configuración global del sistema LPA Aumovio."""

    PROJECT_NAME: str = "Sistema IA de Análisis LPA - Aumovio"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Conexión a BD: Por defecto usa SQLite local en la raíz del backend;
    # en Docker se sobreescribirá automáticamente con PostgreSQL vía variable de entorno.
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'backend' / 'lpa_aumovio.db'}"

    # Contrato de Datos: Hoja y columnas exactas del Excel exportado en Aumovio
    EXCEL_EXPECTED_SHEET: str = "Reporte Discrepancias LPA"
    EXCEL_REQUIRED_COLUMNS: list[str] = [
        "Folio",
        "Área",
        "Tema",
        "Fecha del Hallazgo",
        "Fecha Compromiso de Cierre",
        "Auditor",
        "Responsable de Cierre",
        "Descripción de la Discrepancia",
        "Solución para Cierre",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instancia única (Singleton) para importar en cualquier módulo
settings = Settings()