from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    """Devuelve la fecha y hora actual en UTC con zona horaria."""
    return datetime.now(timezone.utc)


# =====================================================================
# 1. ENTIDAD: REPORTES (Lotes de carga trimestral en Excel)
# =====================================================================
class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    period: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # Ej: "2026-Q3"
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    total_discrepancies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relaciones bidireccionales (1 Reporte -> N Discrepancias y N Top Offenders)
    discrepancies: Mapped[list["Discrepancy"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )
    top_offenders: Mapped[list["TopOffender"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


# =====================================================================
# 2. ENTIDAD: ÁREAS OPERATIVAS (Catálogo normalizado - Columna 'Área')
# =====================================================================
class Area(Base):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)

    discrepancies: Mapped[list["Discrepancy"]] = relationship(back_populates="area")


# =====================================================================
# 3. ENTIDAD: CATEGORÍAS LPA (Catálogo normalizado - Columna 'Tema')
# =====================================================================
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)

    discrepancies: Mapped[list["Discrepancy"]] = relationship(back_populates="category")
    top_offenders: Mapped[list["TopOffender"]] = relationship(back_populates="category")


# =====================================================================
# 4. ENTIDAD: TOP OFFENDERS (Clústeres semánticos detectados por IA)
# =====================================================================
class TopOffender(Base):
    __tablename__ = "top_offenders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)

    # Descripción representativa (Medoide) elegida por el algoritmo NLP
    canonical_description: Mapped[str] = mapped_column(Text, nullable=False)
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    percentage_of_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rank_position: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Vector centroide serializado (JSON) para comparaciones históricas entre trimestres
    centroid_embedding_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    report: Mapped["Report"] = relationship(back_populates="top_offenders")
    category: Mapped["Category"] = relationship(back_populates="top_offenders")
    discrepancies: Mapped[list["Discrepancy"]] = relationship(back_populates="top_offender")


# =====================================================================
# 5. ENTIDAD: DISCREPANCIAS / AUDITORÍAS LPA (Registro individual Excel)
# =====================================================================
class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"), nullable=False, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)

    # Es opcional al momento de la ingesta ETL; se llena cuando corre el motor NLP
    top_offender_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("top_offenders.id"), nullable=True, index=True
    )

    # Metadatos de la auditoría y hallazgo provenientes del Excel de Aumovio
    folio: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    finding_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    commitment_date: Mapped[date] = mapped_column(Date, nullable=False)
    closure_days_sla: Mapped[int] = mapped_column(Integer, nullable=False)  # Días otorgados para cierre
    auditor: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    responsible: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    # Textos para análisis de IA y trazabilidad de cierre
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    clean_description: Mapped[str] = mapped_column(Text, nullable=False)
    closure_solution: Mapped[str] = mapped_column(Text, nullable=False)

    # Vector numérico (Embedding) del hallazgo para cálculo de similitud semántica
    embedding_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones ORM
    report: Mapped["Report"] = relationship(back_populates="discrepancies")
    area: Mapped["Area"] = relationship(back_populates="discrepancies")
    category: Mapped["Category"] = relationship(back_populates="discrepancies")
    top_offender: Mapped[Optional["TopOffender"]] = relationship(back_populates="discrepancies")


# =====================================================================
# 6. ENTIDAD: HISTORIALES (Trazabilidad multiperiodo entre trimestres)
# =====================================================================
class HistoricalTrend(Base):
    __tablename__ = "historical_trends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    current_offender_id: Mapped[int] = mapped_column(
        ForeignKey("top_offenders.id"), nullable=False, index=True
    )
    previous_offender_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("top_offenders.id"), nullable=True, index=True
    )

    similarity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    previous_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delta_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    trend_status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # NUEVO, EN_AUMENTO, EN_DISMINUCION, CONSTANTE