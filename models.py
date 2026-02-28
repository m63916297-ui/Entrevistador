from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class Nivel(str, Enum):
    JUNIOR = "Junior"
    SENIOR = "Senior"
    LEAD = "Lead"


class Recomendacion(str, Enum):
    NO_CUMPLE = "No cumple"
    CUMPLE = " Cumple"
    SOBRECUALIFICADO = "Sobrecualificado"


class PreguntaTecnica(BaseModel):
    pregunta: str = Field(description="La pregunta técnica formulada")
    respuesta_esperada: str = Field(
        description="Respuesta ideal o puntos clave esperados"
    )
    area: str = Field(
        description="Área técnica de la pregunta (ej: Backend, Frontend, Base de Datos)"
    )


class ResultadoEvaluacion(BaseModel):
    pregunta: str
    respuesta_simulada: str
    score_pregunta: int = Field(
        ge=0, le=20, description="Puntuación de 0-20 por pregunta"
    )
    feedback: str = Field(description="Feedback breve de la respuesta")


class EntrevistaOutput(BaseModel):
    rol: str = Field(description="Rol solicitado para la entrevista")
    nivel: Nivel = Field(description="Nivel solicitado")
    stack: List[str] = Field(description="Stack tecnológico del candidato")
    preguntas: List[PreguntaTecnica] = Field(
        description="5 preguntas técnicas generadas"
    )
    respuestas_simuladas: List[ResultadoEvaluacion] = Field(
        description="Evaluación de respuestas simuladas"
    )
    score_tecnico: int = Field(ge=0, le=100, description="Score técnico total (0-100)")
    recomendacion: Recomendacion = Field(
        description="Recomendación final basada en el score"
    )
    resumen: str = Field(description="Resumen ejecutivo de la evaluación")
