from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta, datetime
import subprocess

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
    subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "Airflow\data\webscrapping.ipynb"], check=True)

def run_embedding():
    subprocess.run(["python", "Airflow\data\embedding.py"], check=True)

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

# Puedes agregar una notificación o reinicio de API aquí si es necesario

start >> scrape_data_task >> generate_embeddings_task >> end
