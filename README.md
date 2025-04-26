# 👨‍👩‍👧‍👦 Proyecto LLM: Qué Hacer Con Los Niños

Este proyecto usa técnicas de **Web Scraping**, procesamiento de lenguaje natural (NLP) y un modelo de lenguaje (LLM) para convertir el contenido del sitio [quehacerconlosniños.com](https://quehacerconlosniños.com) en una herramienta interactiva con una interfaz visual en **Streamlit**.

## 🌐 Objetivo

Extraer automáticamente información de artículos del sitio web, procesarla y hacerla accesible mediante una app donde cualquier usuario pueda preguntar sobre planes, eventos y recomendaciones para hacer con niños.

## 🧠 Tecnologías utilizadas

- 🕸️ **Web Scraping** con `requests`, `BeautifulSoup` y `Selenium`
- 🧩 **Chunking y Tokenización** para preparar textos largos para el modelo
- 🧠 **LLM** con embeddings y vector store
- 🎛️ **Streamlit** para la interfaz visual
- 🗃️ **FAISS** para búsqueda semántica eficiente
- 🐍 Jupyter Notebooks para desarrollo modular


## ⚙️ ¿Cómo funciona?

1. **Extracción**: se extrae contenido (títulos, fechas, cuerpos de texto) de los artículos del sitio.
2. **Procesamiento**: se divide el texto en chunks y se tokeniza para permitir consultas eficientes.
3. **Embeddings**: los chunks se convierten en vectores y se almacenan en una base de datos vectorial.
4. **Interfaz**: el usuario hace preguntas a través de Streamlit y el sistema responde usando los artículos más relevantes.
