from datetime import datetime, timedelta

from airflow.operators.bash import BashOperator

from airflow import DAG

# Default DAG args
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# Define DAG
with DAG(
    dag_id="hello_world",
    default_args=default_args,
    description="Simple test DAG",
    schedule_interval="@daily",  # runs once per day
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
    task1 = BashOperator(task_id="print_date", bash_command="date")

    task2 = BashOperator(task_id="say_hello", bash_command="echo 'Hello from Airflow!'")

    task1 >> task2
