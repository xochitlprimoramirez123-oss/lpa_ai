from datetime import date
from pydantic import BaseModel, ConfigDict

class DiscrepancyRaw(BaseModel):
    """
    Esquema Pydantic de transición.
    Garantiza que la fila del Excel tenga los tipos de datos correctos
    antes de ser convertida a un modelo de SQLAlchemy.
    """
    folio: str
    area: str
    category: str
    finding_date: date
    commitment_date: date
    auditor: str
    responsible: str
    raw_description: str
    closure_solution: str

    # Permite a Pydantic leer diccionarios u objetos de bases de datos de forma nativa
    model_config = ConfigDict(from_attributes=True)