# Sistema de IA para Análisis de Discrepancias LPA y Detección de Top Offenders — Aumovio

Sistema integral de Ingeniería de Datos e Inteligencia Artificial (NLP) diseñado para automatizar el procesamiento de reportes de **Auditorías de Procesos por Capas (LPA)** en formato Excel, identificar patrones semánticos recurrentes (*Top Offenders*), analizar tendencias históricas multiperiodo y generar reportes ejecutivos trimestrales para el departamento de Calidad.

## Arquitectura del Proyecto

- **Backend:** Python + FastAPI + SQLAlchemy 2.0 + Pydantic v2
- **Motor ETL y Estadístico:** Pandas + NumPy + OpenPyXL
- **Motor IA / NLP:** Sentence-Transformers + Scikit-Learn (Agrupamiento Semántico Local)
- **Base de Datos:** Relacional (SQLite en desarrollo local / PostgreSQL en contenedor)
- **Infraestructura:** Docker & Docker Compose