from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import subprocess
import os

# ----------------------
# Definir rutas absolutas
# ----------------------
DAG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(DAG_DIR, os.pardir))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
DATA_PATH = os.path.join(SCRIPTS_DIR, 'data', 'Articulos_limpios.csv')
INDEX_PATH = os.path.join(BASE_DIR, 'faiss_index')
SCRAPING_SCRIPT = os.path.join(SCRIPTS_DIR, 'Webscraping.py')
EMBEDDING_SCRIPT = os.path.join(SCRIPTS_DIR, 'embedding.py')

# ----------------------
# Configuración del DAG
# ----------------------
default_args = {
    'owner': 'airflow',
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'update_vectorstore_for_chatbot',
    default_args=default_args,
    description='Scrape, embed and update vectorstore for chatbot daily',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['webscraping', 'chatbot', 'embeddings'],
)

# ----------------------
# Funciones de tareas
# ----------------------

def run_scraping():
    print(f"🚀 Ejecutando scraping desde: {SCRAPING_SCRIPT}")
    subprocess.run(["python", SCRAPING_SCRIPT], check=True)
    print("✅ Webscraping finalizado")

def run_embedding():
    print(f"📂 Verificando existencia del CSV en: {DATA_PATH}")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ CSV no encontrado: {DATA_PATH}")

    print(f"📦 Verificando índice FAISS en: {INDEX_PATH}")
    if not os.path.exists(INDEX_PATH) or os.path.getmtime(DATA_PATH) > os.path.getmtime(INDEX_PATH):
        print("🔁 Ejecutando embedding.py para actualizar vectorstore...")
        subprocess.run(["python", EMBEDDING_SCRIPT], check=True)
        print("✅ Vectorstore actualizado")
    else:
        print("ℹ️ Vectorstore ya está actualizado. No es necesario regenerar.")

# ----------------------
# Definición de tareas
# ----------------------

start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

scrape_data_task = PythonOperator(
    task_id='scrape_data',
    python_callable=run_scraping,
    execution_timeout=timedelta(minutes=90),  # dale más tiempo
    dag=dag,
)

generate_embeddings_task = PythonOperator(
    task_id='generate_embeddings',
    python_callable=run_embedding,
    execution_timeout=timedelta(minutes=15),
    dag=dag,
)

# ----------------------
# Flujo del DAG
# ----------------------
start >> scrape_data_task >> generate_embeddings_task >> end
