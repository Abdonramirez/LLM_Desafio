from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta, datetime
import subprocess
import os 

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_PATH = os.path.join(SCRIPT_DIR, "../scripts")

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
    path = os.path.join(SCRIPTS_PATH, "webscrapping.ipynb")
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", path], check=True)

def run_embedding():
    import os
    if not os.path.exists("faiss_index") or os.path.getmtime("data/Articulos_LLM6.csv") > os.path.getmtime("faiss_index"):
        subprocess.run(["python", "Airflow/scripts/embedding.py"], check=True)
    else:
        print("ℹ️ Vectorstore ya actualizado, se omite regeneración.")

def restart_fastapi():
    try:
        subprocess.run(["docker", "restart", "ollama_agent_api"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error reiniciando API: {e}")
        raise

start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

restart_task = PythonOperator(
    task_id="restart_chatbot_api",
    python_callable=restart_fastapi,
    dag=dag,
)

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

# Puedes agregar una notificación o reinicio de API aquí si es necesario

start >> scrape_data_task >> generate_embeddings_task >> restart_task >> end
