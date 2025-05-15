from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import subprocess
import os

# Definir rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_PATH = os.path.join(SCRIPT_DIR, "../scripts")
DATA_PATH = os.path.join(SCRIPT_DIR, "../data/Articulos_limpios.csv")
INDEX_PATH = os.path.join(SCRIPT_DIR, "../faiss_index")
EMBEDDING_SCRIPT = os.path.join(SCRIPTS_PATH, "embedding.py")
SCRAPING_SCRIPT = os.path.join(SCRIPTS_PATH, "Webscraping.py")

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
    schedule_interval='@daily',  # o '0 6 * * *' para 6 am
    start_date=days_ago(1),
    catchup=False,
    tags=['webscraping', 'chatbot', 'embeddings'],
)

def run_scraping():
    path = os.path.join(SCRIPTS_PATH, "Webscraping.py")
    subprocess.run(["python", path], check=True)

def run_embedding():
    try:
        if not os.path.exists(INDEX_PATH) or os.path.getmtime(DATA_PATH) > os.path.getmtime(INDEX_PATH):
            subprocess.run(["python", EMBEDDING_SCRIPT], check=True)
        else:
            print("ℹ️ Vectorstore ya actualizado, se omite regeneración.")
    except Exception as e:
        print(f"❌ Error en embedding: {e}")
        raise

start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

scrape_data_task = PythonOperator(
    task_id='scrape_data',
    python_callable=run_scraping,
    dag=dag,
)

generate_embeddings_task = PythonOperator(
    task_id='generate_embeddings',
    python_callable=run_embedding,
    dag=dag,
)

# Define flujo del DAG
start >> scrape_data_task >> generate_embeddings_task >> end
