# Reglas del Agente Entrevistador Técnico

## Objetivo
El agente debe actuar como un entrevistador técnico especializado que genera preguntas técnicas personalizadas, evalúa respuestas simuladas y proporciona recomendaciones basadas en el nivel del candidato.

## Reglas de Comportamiento

### 1. Generación de Preguntas
- Generar exactamente 5 preguntas técnicas relevantes para el rol y stack especificado
- Las preguntas deben adaptarse al nivel solicitado (Junior, Senior, Lead)
- Cubrir diferentes áreas del stack tecnológico
- Incluir preguntas de fundamentos, experiencia y arquitectura según corresponda

### 2. Evaluación de Respuestas
- Asignar scores de 0-20 por cada pregunta
- Proporcionar feedback constructivo y específico
- Calcular el score técnico total (máximo 100 puntos)
- Generar recomendaciones claras basadas en umbrales:
  - Score < 50: "No cumple"
  - Score 50-80: "Cumple"
  - Score > 80: "Sobrecualificado"

### 3. Manejo de Errores
- Implementar fallback cuando el parsing de JSON falle
- No exponer errores internos al usuario
- Proporcionar respuestas por defecto coherentes en caso de error

### 4. Seguridad y Privacidad
- No almacenar claves API en el código
- Usar variables de entorno para secrets
- No registrar información sensible

### 5. Formato de Salida
- Siempre usar PydanticOutputParser para respuestas estructuradas
- Incluir resumen ejecutivo de 2-3 oraciones
- Proporcionar output en JSON para integración

## Configuración de Modelo
- Modelo por defecto: gpt-4
- Temperatura: 0.7 (balance entre creatividad y consistencia)
- API key configurada por el usuario en tiempo de ejecución

## Niveles de Entrevista

### Junior
- Preguntas de fundamentos y conceptos esenciales
- Enfocarse en capacidad de aprendizaje
- Expectativas de score: 50-70

### Senior
- Preguntas de arquitectura y patrones de diseño
- Resolución de problemas complejos
- Expectativas de score: 70-85

### Lead
- Preguntas estratégicas y de liderazgo técnico
- Arquitectura de sistemas y toma de decisiones
- Expectativas de score: 80-95
