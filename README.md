# Entrevistador Técnico IA

Aplicación web desarrollada con Streamlit que funciona como un agente de entrevista técnica basado en inteligencia artificial. El agente genera preguntas técnicas personalizadas según el rol, nivel y stack tecnológico solicitado, evalúa respuestas simuladas y proporciona un score técnico con recomendaciones.

## Características

- **Generación de Preguntas Técnicas**: Crea 5 preguntas personalizadas según el perfil del candidato
- **Evaluación Automática**: Asigna scores de 0-20 por pregunta con feedback detallado
- **Múltiples Roles Soportados**: Full Stack, Backend, Frontend, Data Engineer, DevOps, Arquitecto, ML Engineer, Security Engineer
- **Tres Niveles**: Junior, Senior y Lead con preguntas adaptadas a cada nivel
- **Output JSON Estructurado**: Facilita la integración con otros sistemas

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI                          │
│                    (app.py - 170 líneas)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  EntrevistadorAgente                        │
│                 (agente.py - 246 líneas)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Generación  │  │   Respuestas │  │  Evaluación  │
│  │  de Preguntas │  │  Simuladas   │  │    Final     │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           ▼                                 │
│              ┌────────────────────────┐                     │
│              │   ChatOpenAI (GPT-4)   │                     │
│              │  PydanticOutputParser  │                     │
│              └────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Models (Pydantic)                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │
│  │   Nivel    │ │Recomendacion│ │Pregunta    │ │Resultado │ │
│  │  (Enum)    │ │  (Enum)    │ │Tecnica     │ │Evaluacion│ │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘ │
│                                                             │
│              EntrevistaOutput (Schema Principal)            │
└─────────────────────────────────────────────────────────────┘
```

## Componentes

### 1. app.py (Interfaz de Usuario)

Interfaz web construida con Streamlit que proporciona:

- **Formulario de Configuración**: Selección de rol, nivel y stack tecnológico
- **Entrada de API Key**: Configuración de credenciales OpenAI
- **Visualización de Resultados**: Métricas, progress bar, expaders para preguntas/respuestas
- **Output JSON**: Código formateado con la estructura completa de la entrevista

**Roles disponibles:**
- Desarrollador Full Stack
- Desarrollador Backend
- Desarrollador Frontend
- Ingeniero de Datos
- DevOps Engineer
- Arquitecto de Software
- ML Engineer
- Security Engineer

**Stack tecnológico soportado:**
- Python, JavaScript, TypeScript, Java, Go, Rust
- React, Vue, Angular, Node.js
- Django, FastAPI
- PostgreSQL, MongoDB, Redis
- Docker, Kubernetes
- AWS, Azure, GCP
- GraphQL, REST API

### 2. agente.py (Lógica del Agente)

Clase principal `EntrevistadorAgente` que implementa el flujo de entrevista:

#### Métodos principales:

- `ejecutar_entrevista(rol, nivel, stack)`: Orquestra todo el proceso
- `_generar_prompt_preguntas()`: Crea el prompt para generar 5 preguntas técnicas
- `_generar_prompt_respuestas()`: Genera respuestas simuladas con scores
- `_generar_prompt_evaluacion()`: Calcula el score total y recomendaciónacterísticas técnicas:

- **Modelo

#### Car**: GPT-4 por defecto (configurable)
- **Temperatura**: 0.7 (balance creatividad/consistencia)
- **Parser**: PydanticOutputParser para respuestas estructuradas
- **Fallback**: Sistema de recuperación ante errores de parsingógica de evaluación

#### L:

| Score Total|-------------|------------ | Recomendación |
---|
| < 50        | No cumple     |
| 50 - 80     | Cumple        |
| > 80        | Sobrecualificado |

### 3. models.py ( Esquemas de Datos)

Definiciones Pydantic para validación de datos:

```python
Nivel (Enum): JUNIOR, SENIOR, LEAD

Recomendacion (Enum): NO_CUMPLE, CUMPLE, SOBRECUALIFICADO

PreguntaTecnica:
  - pregunta: str
  - respuesta_esperada: str
  - area: str

ResultadoEvaluacion:
  - pregunta: str
  - respuesta_simulada: str
  - score_pregunta: int (0-20)
  - feedback: str

EntrevistaOutput:
  - rol: str
  - nivel: Nivel
  - stack: List[str]
  - preguntas: List[PreguntaTecnica]
  - respuestas_simuladas: List[ResultadoEvaluacion]
  - score_tecnico: int (0-100)
  - recomendacion: Recomendacion
  - resumen: str
```

## Detalles Técnicos

### Dependencias

```
langchain==0.3.17
langchain-openai==0.2.14
pydantic==2.10.6
streamlit==1.42.0
openai==1.58.1
toml>=0.10.2
```

### Configuración de Modelo

- **Modelo por defecto**: `gpt-4`
- **Temperatura**: `0.7`
- **API Key**: Configurable via variables de entorno o entrada del usuario

### Niveles de Preguntas

| Nivel   | Tipo de Preguntas                          | Expectativa Score |
|---------|-------------------------------------------|-------------------|
| Junior  | Fundamentos y conceptos esenciales       | 50-70             |
| Senior  | Arquitectura y patrones de diseño        | 70-85             |
| Lead    | Estrategia y liderazgo técnico            | 80-95             |

### Manejo de Errores

El agente implementa un sistema de fallback robusto:

1. **Parsing JSON Fallido**: Genera preguntas base predefinidas
2. **Error en Respuestas**: Scores por defecto según nivel
3. **Error en Evaluación**: Calcula score total desde respuestas existentes

## Instalación y Uso

### Requisitos Previos

- Python 3.8+
- API Key de OpenAI

### Instalación Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variable de entorno
export OPENAI_API_KEY="tu-api-key"  # Linux/Mac
set OPENAI_API_KEY=tu-api-key       # Windows

# Ejecutar aplicación
streamlit run app.py
```

### Despliegue en Streamlit Cloud

1. Subir código a repositorio GitHub
2. Crear app en [Streamlit Cloud](https://streamlit.io/cloud)
3. Configurar secrets:
   ```toml
   OPENAI_API_KEY = "tu-api-key"
   ```
4. Desplegar

## Estructura de Archivos

```
entrevistador/
├── app.py                 # Interfaz Streamlit
├── agente.py              # Lógica del agente
├── models.py              # Modelos Pydantic
├── requirements.txt       # Dependencias
├── AGENT_RULES.md         # Reglas del agente
├── SECRETS.md            # Configuración de secrets
├── .streamlit/           # Configuración Streamlit
└── .venv/                # Entorno virtual
```

## Consideraciones de Seguridad

- **API Keys**: Nunca almacenar en código fuente
- **Variables de Entorno**: Usar para configuración sensible
- **Streamlit Secrets**: Recomendado para producción
- **Logs**: Evitar registrar información sensible

## Extensiones Futuras

- Integración con entrevistas reales (no simuladas)
- Historial de entrevistas por candidato
- Exportación a PDF
- Múltiples idiomas
- Evaluación de soft skills
- Integración con ATS (Applicant Tracking Systems)
