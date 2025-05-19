FROM apache/airflow:2.9.0

USER root

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_airflow.txt /requirements_airflow.txt
USER airflow
RUN pip install --no-cache-dir -r /requirements_airflow.txt
