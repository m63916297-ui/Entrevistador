import streamlit as st
import json
import os
from agente import crear_agente, EntrevistadorAgente
from models import EntrevistaOutput, Nivel, Recomendacion


def load_secrets():
    """Carga la API key desde secrets de Streamlit Cloud o variables de entorno."""
    if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return os.environ.get("OPENAI_API_KEY", "")


st.set_page_config(
    page_title="Entrevistador Técnico IA", page_icon="👨‍💻", layout="wide"
)


def inicializar_estado():
    if "resultado" not in st.session_state:
        st.session_state.resultado = None
    if "api_key" not in st.session_state:
        st.session_state.api_key = load_secrets()


def mostrar_formulario() -> tuple:
    st.header("📋 Configuración de la Entrevista")

    col1, col2 = st.columns(2)

    with col1:
        rol = st.selectbox(
            "Rol Solicitado",
            [
                "Desarrollador Full Stack",
                "Desarrollador Backend",
                "Desarrollador Frontend",
                "Ingeniero de Datos",
                "DevOps Engineer",
                "Arquitecto de Software",
                "ML Engineer",
                "Security Engineer",
            ],
        )

        nivel = st.selectbox("Nivel", ["Junior", "Senior", "Lead"])

    with col2:
        stack_opciones = [
            "Python",
            "JavaScript",
            "TypeScript",
            "Java",
            "Go",
            "Rust",
            "React",
            "Vue",
            "Angular",
            "Node.js",
            "Django",
            "FastAPI",
            "PostgreSQL",
            "MongoDB",
            "Redis",
            "Docker",
            "Kubernetes",
            "AWS",
            "Azure",
            "GCP",
            "GraphQL",
            "REST API",
        ]

        stack = st.multiselect(
            "Stack Tecnológico",
            stack_opciones,
            default=["Python", "JavaScript", "PostgreSQL"],
        )

    api_key = st.text_input(
        "API Key de OpenAI",
        type="password",
        value=st.session_state.api_key,
        help="Ingresa tu API key de OpenAI o configúrala en los secrets de Streamlit Cloud",
    )

    return rol, nivel, stack, api_key


def mostrar_resultado(resultado: EntrevistaOutput):
    st.divider()

    st.header("📊 Resultados de la Entrevista")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rol", resultado.rol)
    with col2:
        st.metric("Nivel", resultado.nivel.value)
    with col3:
        color = "normal"
        if resultado.recomendacion == Recomendacion.NO_CUMPLE:
            color = "off"
        elif resultado.recomendacion == Recomendacion.SOBRECUALIFICADO:
            color = "inverse"
        st.metric("Recomendación", resultado.recomendacion.value, delta_color=color)

    st.subheader(f"🎯 Score Técnico: {resultado.score_tecnico}/100")

    barra_score = st.progress(resultado.score_tecnico)

    st.subheader("📝 Preguntas y Respuestas")

    for i, (preg, resp) in enumerate(
        zip(resultado.preguntas, resultado.respuestas_simuladas), 1
    ):
        with st.expander(f"Pregunta {i}: {preg.area}"):
            st.markdown(f"**Pregunta:** {preg.pregunta}")
            st.markdown(f"**Respuesta Esperada:** {preg.respuesta_esperada}")
            st.markdown("---")
            st.markdown(f"**Respuesta Simulada:** {resp.respuesta_simulada}")
            st.markdown(f"**Score:** {resp.score_pregunta}/20")
            st.markdown(f"**Feedback:** {resp.feedback}")

    st.subheader("📋 Resumen Ejecutivo")
    st.info(resultado.resumen)

    st.subheader("🔧 Output JSON Estructurado")
    st.code(resultado.model_dump_json(indent=2), language="json")


def main():
    inicializar_estado()

    st.title("👨‍💻 Entrevistador Técnico IA")
    st.markdown("""
    Este agente genera preguntas técnicas personalizadas basadas en el rol, 
    nivel y stack tecnológico solicitado, evalúa las respuestas y proporciona 
    un score técnico con recomendaciones.
    """)

    rol, nivel, stack, api_key = mostrar_formulario()

    if st.button("🚀 Iniciar Entrevista", type="primary"):
        if not api_key:
            st.error("Por favor ingresa tu API key de OpenAI")
            return

        if not stack:
            st.error("Por favor selecciona al menos una tecnología del stack")
            return

        with st.spinner("Generando preguntas técnicas y evaluando respuestas..."):
            try:
                agente = crear_agente(api_key)
                resultado = agente.ejecutar_entrevista(rol, nivel, stack)
                st.session_state.resultado = resultado
            except Exception as e:
                st.error(f"Error al ejecutar la entrevista: {str(e)}")
                return

    if st.session_state.resultado:
        mostrar_resultado(st.session_state.resultado)


if __name__ == "__main__":
    main()
