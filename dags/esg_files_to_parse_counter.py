from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner':'airflow',
    'depends_on_past': False,
    'retries':1,
    'retry_delay':timedelta(minutes=5)    
}

def count_ESG_companies():
    hook = PostgresHook(postgres_conn_id='esg_postgres')
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM company_esg_scores;')
    count = cursor.fetchone()[0]
    print(f"Number of companies currently on ESG database: {count}")
    
with DAG(
    'esg_company_counter', #name of dag
    default_args = default_args,
    description = "Count number of companies in esgdatabase, every hour",
    schedule_interval = '@hourly',
    start_date = datetime(2025,9,15),
    catchup=False,
) as dag:
    
    t1 = PythonOperator(
        task_id = 'count_ESG_companies', #name of task id
        python_callable=count_ESG_companies # def to run for this task id
    )