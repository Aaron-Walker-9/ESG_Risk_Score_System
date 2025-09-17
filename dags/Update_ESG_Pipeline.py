#Airflow DAG for regularly updating ESG inference pipline: every 20 min
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
import logging
from datetime import datetime, timedelta
from esg_risk_score_system.main import run_pipeline

default_args = {
    'owner':'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay':timedelta(minutes = 1)
}

def process_pending():
    logger = logging.getLogger("airflow.task")
    # try, except, finally: to give error logging if process fails
    try:
        hook = PostgresHook(postgres_conn_id = "esg_postgres")
        conn = hook.get_conn()
        cur = conn.cursor()

        cur.execute("SELECT url FROM company_pdfs WHERE status='pending'")
        rows = cur.fetchall()

        if not rows:
            print("No pending companies to process.")
            return

        urls = [row[0] for row in rows]
        logger.error(f"Processing {len(urls)} companies")

        run_pipeline(urls, conn, cur)

        for row in rows:
            cur.execute("UPDATE company_pdfs SET status='processed' WHERE url=%s", (row[0],))
        conn.commit()
        logger.info("Finished processing pending companies and updated company statuses.")
        
    except Exception as e:
        logger.info(f"Failed to process: {str(e)}", exc_info=True)
        raise
    
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()
            
        logger.info("Database connection closed.")
        
    

with DAG(
    'ESG_Pipeline_Update',
    default_args = default_args,
    description = "Updates esg risk scores for pending companies",
    schedule_interval = timedelta(minutes = 20), # run every 20min after initialisation
    start_date = datetime(2025,9,17),
    catchup = False,
) as dag:

    t1 = PythonOperator(
        task_id = 'Update_pending_companies',
        python_callable = process_pending
    )