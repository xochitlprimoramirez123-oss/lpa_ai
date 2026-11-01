import pandas as pd
from pathlib import Path

from app.core.config import settings
from app.schemas.lpa_schemas import DiscrepancyRaw

class ETLService:
    @staticmethod
    def process_excel(file_path: Path | str) -> list[DiscrepancyRaw]:
        """
        Lee el Excel de Aumovio, normaliza columnas, limpia texto y retorna
        una lista validada de objetos Pydantic.
        """
        # 1. EXTRACCIÓN (Fail-Fast)
        try:
            df = pd.read_excel(file_path, sheet_name=settings.EXCEL_EXPECTED_SHEET)
        except ValueError:
            raise ValueError(f"El archivo debe contener una hoja llamada '{settings.EXCEL_EXPECTED_SHEET}'")

        missing_cols = [col for col in settings.EXCEL_REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"El Excel no tiene el formato oficial. Faltan columnas: {missing_cols}")

        # 2. TRANSFORMACIÓN (Limpieza Vectorizada)
        # 2.1 Mapear columnas del español del Excel a las variables internas en inglés
        column_mapping = {
            "Folio": "folio",
            "Área": "area",
            "Tema": "category",
            "Fecha del Hallazgo": "finding_date",
            "Fecha Compromiso de Cierre": "commitment_date",
            "Auditor": "auditor",
            "Responsable de Cierre": "responsible",
            "Descripción de la Discrepancia": "raw_description",
            "Solución para Cierre": "closure_solution"
        }
        df = df.rename(columns=column_mapping)
        
        # Quedarnos solo con las columnas que nos importan
        df = df[list(column_mapping.values())]

        # 2.2 Limpiar textos: Eliminar espacios en blanco al inicio/final y convertir a string
        text_cols = ["folio", "area", "category", "auditor", "responsible", "raw_description", "closure_solution"]
        for col in text_cols:
            df[col] = df[col].astype(str).str.strip()

        # 2.3 Convertir fechas usando el parser avanzado de Pandas
        df['finding_date'] = pd.to_datetime(df['finding_date']).dt.date
        df['commitment_date'] = pd.to_datetime(df['commitment_date']).dt.date

        # 3. CARGA EN MEMORIA (Validación con Pydantic)
        # Convertimos el DataFrame a una lista de diccionarios
        records = df.to_dict(orient="records")
        
        # Pasamos cada diccionario al esquema Pydantic para asegurar que cumple los tipos
        validated_data = [DiscrepancyRaw(**record) for record in records]

        return validated_data