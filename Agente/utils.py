import os
import streamlit as st
from typing import List
from langchain.schema import BaseMessage, HumanMessage, AIMessage

def cargar_estilos(ruta: str) -> None:
    """Incorpora una hoja de estilos en la página de Streamlit."""
    with open(ruta, "r") as f:
        st.markdown(
            f"""<style>{f.read()}</style>""",
            unsafe_allow_html=True,
        )


def guia_de_uso():
    with st.expander("📌 **Guía de uso del chatbot**"):
        col_izq, col_der = st.columns(2)

        with col_izq:
            st.success(
                """
                ✅ **¿Qué puedo hacer por ti?**

                - Respondo preguntas usando información contextual de los documentos disponibles.
                - Te ayudo con dudas generales relacionadas con actividades infantiles y familiares.
                - Puedo recuperar y mostrar contenido útil desde la base de datos de ocio.
                """
            )

        with col_der:
            st.error(
                """
                ⚠️ **Limitaciones**

                - Mis respuestas dependen de los documentos cargados en la base de datos.
                - Puede que no entienda saludos o frases muy generales si no hay contexto relacionado.
                - Para mejores resultados, escribe preguntas claras y concretas.
                """
            )

        st.info(
            """
            💬 **Ejemplos de preguntas**

            > ¿Qué planes hay para este fin de semana en Madrid?

            > ¿Recomiendas alguna actividad gratuita con niños pequeños?

            > ¿Cuáles son los eventos destacados en abril?
            """
        )


def mensaje_usuario(contenido: str):
    with st.chat_message("user", avatar=os.path.join(os.path.dirname(__file__), '../static/img/user.svg')):
        st.markdown(contenido)


def mensaje_bot(contenido: str):
    with st.chat_message("assistant", avatar=os.path.join(os.path.dirname(__file__), '../static/img/bot.png')):
        st.markdown(contenido)


def historial_chat(historial: List[BaseMessage]):
    for mensaje in historial:
        if isinstance(mensaje, HumanMessage):
            mensaje_usuario(mensaje.content)
        elif isinstance(mensaje, AIMessage):
            mensaje_bot(mensaje.content)

