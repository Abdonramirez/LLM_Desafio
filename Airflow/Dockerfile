FROM apache/airflow:2.9.0

USER root

# Instala librerías necesarias (si realmente las necesitas)
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copia el requirements.txt
COPY requirements.txt /requirements_airflow.txt

# ⚠ Cambiar a usuario 'airflow' antes de instalar
USER airflow

# Instala los paquetes Python como usuario permitido
RUN pip install --no-cache-dir -r /requirements_airflow.txt
