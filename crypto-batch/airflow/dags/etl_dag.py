from datetime import datetime, timedelta

from airflow.operators.empty import EmptyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from airflow import DAG

# Default DAG args
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="etl_spark",
    default_args=default_args,
    description="ETL DAG running Spark job",
    schedule_interval="@daily",  # runs once per day
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["spark", "etl"],
) as dag:
    start = EmptyOperator(task_id="start")

    spark_job = SparkSubmitOperator(
        task_id="run_spark_etl",
        application="/data/landing_job.py",  # path inside Airflow container
        conn_id="spark_default",  # defined in Airflow connections
        name="LandingZone",
        verbose=True,
        conf={
            "spark.hadoop.fs.s3a.access.key": "minioadmin",
            "spark.hadoop.fs.s3a.secret.key": "minioadmin",
            "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
            "spark.hadoop.fs.s3a.path.style.access": "true",
        },
        jars="/opt/spark-extra-jars/hadoop-aws-3.3.4.jar,/opt/spark-extra-jars/aws-java-sdk-bundle-1.12.262.jar",
        application_args=["2025-08-01"],  # pass parameters if needed
    )

    end = EmptyOperator(task_id="end")
    start >> spark_job >> end  # type: ignore
