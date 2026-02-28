import json
import os
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from models import (
    EntrevistaOutput,
    PreguntaTecnica,
    ResultadoEvaluacion,
    Nivel,
    Recomendacion,
)


class EntrevistadorAgente:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError(
                "API key de OpenAI no proporcionada. Configura OPENAI_API_KEY como variable de entorno o pásala como parámetro."
            )
        self.llm = ChatOpenAI(model=model, api_key=api_key, temperature=0.7)
        self.parser = PydanticOutputParser(pydantic_object=EntrevistaOutput)

    def _generar_prompt_preguntas(self, rol: str, nivel: str, stack: List[str]) -> str:
        stack_str = ", ".join(stack)

        nivel_instruccion = {
            "Junior": "Preguntas básicas y de fundamentos. Enfocarse en conceptos esenciales y capacidad de aprendizaje.",
            "Senior": "Preguntas avanzadas de arquitectura, patrones de diseño y resolución de problemas complejos.",
            "Lead": "Preguntas estratégicas de liderazgo técnico, arquitectura de sistemas y toma de decisiones técnicas.",
        }

        return f"""Eres un entrevistador técnico especializado en evaluar candidatos para roles de tecnología.

Genera 5 preguntas técnicas específicas para el rol de {rol} con nivel {nivel}.
Stack tecnológico: {stack_str}

{nivel_instruccion.get(nivel, nivel_instruccion["Junior"])}

Las preguntas deben:
1. Ser relevantes para el stack tecnológico especificado
2. Estar claramente formuladas
3. Cubrir diferentes áreas del stack
4. Ser apropiadas para el nivel solicitado

Para cada pregunta, proporciona también la respuesta esperada o puntos clave que debería mencionar el candidato.

Responde en formato JSON con el siguiente esquema:
{self.parser.get_format_instructions()}

Incluye las preguntas generadas en el campo "preguntas"."""

    def _generar_prompt_respuestas(
        self, rol: str, nivel: str, stack: List[str], preguntas: List[dict]
    ) -> str:
        return f"""Dado el siguiente contexto de entrevista:
- Rol: {rol}
- Nivel: {nivel}
- Stack: {", ".join(stack)}

Y las siguientes preguntas técnicas:
{json.dumps(preguntas, indent=2, ensure_ascii=False)}

Genera respuestas simuladas realistas para cada pregunta. Las respuestas deben ser:
- Breves pero completas (2-4 oraciones)
- Demuestran el nivel de conocimiento esperado para el nivel {nivel}
- Coherentes con el stack proporcionado

Para cada pregunta, proporciona también:
- Un score de 0-20 basado en la calidad de la respuesta
- Un feedback breve explicando el score

Responde en formato JSON con el siguiente esquema:
{self.parser.get_format_instructions()}"""

    def _generar_prompt_evaluacion(
        self,
        rol: str,
        nivel: str,
        stack: List[str],
        preguntas: List[dict],
        respuestas: List[dict],
    ) -> str:
        return f"""Evalúa las siguientes respuestas simuladas para una entrevista de {
            rol
        } nivel {nivel}.

Stack tecnológico: {", ".join(stack)}

Preguntas y respuestas:
{
            json.dumps(
                [
                    {
                        "pregunta": p["pregunta"],
                        "respuesta": r["respuesta_simulada"],
                        "score": r["score_pregunta"],
                    }
                    for p, r in zip(preguntas, respuestas)
                ],
                indent=2,
                ensure_ascii=False,
            )
        }

Basándote en los scores individuales (cada uno de 0-20), calcula:
1. Score técnico total (suma de los 5 scores, máximo 100)
2. Una recomendación final:
   - "No cumple": score < 50
   - "Cumple": score entre 50 y 80
   - "Sobrecualificado": score > 80

3. Un resumen ejecutivo de la evaluación (2-3 oraciones)

Responde en formato JSON con el siguiente esquema:
{self.parser.get_format_instructions()}"""

    def ejecutar_entrevista(
        self, rol: str, nivel: str, stack: List[str]
    ) -> EntrevistaOutput:
        nivel_enum = Nivel(nivel.capitalize())

        prompt_preguntas = self._generar_prompt_preguntas(rol, nivel, stack)
        response_preguntas = self.llm.invoke(prompt_preguntas)

        try:
            preguntas_data = self.parser.parse(response_preguntas.content)
            preguntas_list = [p.dict() for p in preguntas_data.preguntas]
        except Exception as e:
            print(f"Error parseando preguntas: {e}")
            preguntas_list = self._generar_preguntas_fallback(rol, nivel, stack)

        prompt_respuestas = self._generar_prompt_respuestas(
            rol, nivel, stack, preguntas_list
        )
        response_respuestas = self.llm.invoke(prompt_respuestas)

        try:
            respuestas_data = self.parser.parse(response_respuestas.content)
            respuestas_list = [r.dict() for r in respuestas_data.respuestas_simuladas]
        except Exception as e:
            print(f"Error parseando respuestas: {e}")
            respuestas_list = self._generar_respuestas_fallback(preguntas_list, nivel)

        prompt_evaluacion = self._generar_prompt_evaluacion(
            rol, nivel, stack, preguntas_list, respuestas_list
        )
        response_evaluacion = self.llm.invoke(prompt_evaluacion)

        try:
            evaluacion_data = self.parser.parse(response_evaluacion.content)
            return evaluacion_data
        except Exception as e:
            print(f"Error en evaluación final: {e}")
            return self._evaluacion_fallback(
                rol, nivel_enum, stack, preguntas_list, respuestas_list
            )

    def _generar_preguntas_fallback(
        self, rol: str, nivel: str, stack: List[str]
    ) -> List[dict]:
        preguntas_base = [
            {
                "pregunta": f"¿Cuáles son las principales tecnologías en tu stack de {stack[0] if stack else 'desarrollo'}?",
                "respuesta_esperada": "Debe demostrar conocimiento profundo de las tecnologías principales del stack",
                "area": "Fundamentos",
            },
            {
                "pregunta": f"Describe un desafío técnico reciente que hayas enfrentado trabajando con {stack[0] if stack else 'tu rol'}.",
                "respuesta_esperada": "Debe mostrar capacidad de resolución de problemas",
                "area": "Experiencia",
            },
            {
                "pregunta": "¿Cómo manejas el trabajo en equipo en proyectos técnicos?",
                "respuesta_esperada": "Debe demostrar habilidades de comunicación y colaboración",
                "area": "Soft Skills",
            },
            {
                "pregunta": "¿Cuál es tu enfoque para mantenerte actualizado con las nuevas tecnologías?",
                "respuesta_esperada": "Debe mostrar compromiso con el aprendizaje continuo",
                "area": "Desarrollo Profesional",
            },
            {
                "pregunta": f"¿Cómo diseñarías una arquitectura básica para una aplicación usando {stack[0] if stack else 'tecnologías modernas'}?",
                "respuesta_esperada": "Debe demostrar conocimiento de patrones de diseño y arquitectura",
                "area": "Arquitectura",
            },
        ]
        return preguntas_base[:5]

    def _generar_respuestas_fallback(
        self, preguntas: List[dict], nivel: str
    ) -> List[dict]:
        score_base = {"Junior": 12, "Senior": 16, "Lead": 18}
        score = score_base.get(nivel, 12)

        respuestas = []
        for p in preguntas:
            respuestas.append(
                {
                    "pregunta": p["pregunta"],
                    "respuesta_simulada": f"Respuesta de nivel {nivel} que demuestra conocimiento apropiado para el rol.",
                    "score_pregunta": score,
                    "feedback": f"Respuesta adecuada para el nivel {nivel}.",
                }
            )
        return respuestas

    def _evaluacion_fallback(
        self,
        rol: str,
        nivel: Nivel,
        stack: List[str],
        preguntas: List[dict],
        respuestas: List[dict],
    ) -> EntrevistaOutput:
        score_total = sum(r["score_pregunta"] for r in respuestas)

        if score_total < 50:
            recomendacion = Recomendacion.NO_CUMPLE
        elif score_total <= 80:
            recomendacion = Recomendacion.CUMPLE
        else:
            recomendacion = Recomendacion.SOBRECUALIFICADO

        preguntas_obj = [PreguntaTecnica(**p) for p in preguntas]
        respuestas_obj = [ResultadoEvaluacion(**r) for r in respuestas]

        return EntrevistaOutput(
            rol=rol,
            nivel=nivel,
            stack=stack,
            preguntas=preguntas_obj,
            respuestas_simuladas=respuestas_obj,
            score_tecnico=score_total,
            recomendacion=recomendacion,
            resumen=f"El candidato demuestra conocimientos {recomendacion.value} para el rol de {rol} nivel {nivel.value}.",
        )


def crear_agente(api_key: Optional[str] = None) -> EntrevistadorAgente:
    return EntrevistadorAgente(api_key=api_key)
