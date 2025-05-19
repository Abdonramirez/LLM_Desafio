# 👨‍👩‍👧‍👦 Proyecto LLM: Qué Hacer Con Los Niños

Este proyecto combina **Web Scraping**, **procesamiento de lenguaje natural (NLP)** y un **modelo de lenguaje (LLM)** para transformar el contenido del sitio [quehacerconlosniños.com](https://quehacerconlosniños.com) en una herramienta interactiva accesible a través de un agente conversacional y una **API propia** construida con **FastAPI**. El sistema completo está contenedorizado con Docker, lo que permite una fácil integración y despliegue en entornos de producción y en la nube. Especialmente, Apache Airflow se ejecuta dentro de contenedores Docker, lo que garantiza una arquitectura robusta, escalable y lista para ejecuciones automatizadas 24/7.

---

## 🌐 Objetivo

Extraer automáticamente información de artículos del sitio web, procesarla mediante técnicas de NLP y ponerla a disposición de los usuarios a través de consultas naturales sobre actividades, eventos y recomendaciones para hacer con niños.

---

## 🧠 Tecnologías utilizadas

* 🕸️ **Web Scraping** con `requests`, `BeautifulSoup` y `Selenium`
* 🧹 **Chunking y Tokenización** para textos largos
* 🧠 **LLM** (con embeddings, `HuggingFace` y `Ollama`)
* 📃 **FAISS** como base de datos vectorial
* 🧲 **Jupyter Notebooks** para exploración inicial
* 🧰 **Apache Airflow** para automatización de flujos ETL
* 🐳 **Docker** para contenerización de Airflow y despliegue en la nube
* 💬 **Telegram Bot** para interacción conversacional
* 🚀 **FastAPI** para construir una **API** que permite consultar el sistema de manera programática

---

## ⚙️ ¿Cómo funciona?

1. **Extracción**: Se scrapea contenido (títulos, fechas, cuerpos) del sitio web.
2. **Procesamiento**: Se limpian los textos, se dividen en chunks y se tokenizan.
3. **Embeddings**: Los textos procesados se transforman en vectores y se almacenan con FAISS.
4. **Automatización con Airflow**: Todo el proceso se ejecuta automáticamente mediante DAGs diarios gestionados con Apache Airflow, dentro de contenedores Docker listos para producción.
5. **Interacción múltiple**:
   * A través de **Telegram**, pueden preguntar directamente desde su móvil.
   * A través de **FastAPI**, otros sistemas pueden integrarse fácilmente enviando consultas vía HTTP.

---

## 📁 Estructura del Proyecto

| Carpeta                | Descripción                                                                                                                                                          |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Agente/**                      | Código del agente conversacional implementado con **Telegram** y **Ollama** (modelo Mistral). Maneja el flujo de interacción con el usuario.                         |
| **Airflow/**                     | DAGs y scripts del pipeline automatizado con **Apache Airflow**: scraping, embeddings y actualización diaria. Configurado con **Docker** para producción en la nube. |
| **data/**                        | Contiene los datos estructurados del scraping y la base de datos de conversaciones del agente.                                                                       |
| **static/**                      | Recursos estáticos del proyecto (imágenes, archivos auxiliares, etc.).                                                                                               |
| **WebScrapping/**                | Notebooks de desarrollo y pruebas iniciales del scraping, antes de ser migrado a Airflow.                                                                            |
| **main.py**                      | Punto de entrada del proyecto, permite levantar el sistema o partes específicas (como el agente o la API).                                                           |
| **README.md**                    | Documentación del proyecto (este archivo).                                                                                                                           |
| **pyproject.toml**  | Archivos para la gestión del entorno con `uv`.                                                                                                                       |
