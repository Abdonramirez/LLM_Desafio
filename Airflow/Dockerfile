FROM apache/airflow:2.9.0

USER root

# Instala librerías necesarias
RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    build-essential \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Instala Jupyter y dependencias de scraping/vectorstore
COPY scripts/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

USER airflow
