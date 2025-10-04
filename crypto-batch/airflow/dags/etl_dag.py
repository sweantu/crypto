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

    landing_job = SparkSubmitOperator(
        task_id="landing_job",
        application="/data/landing_job.py",  # path inside Airflow container
        conn_id="spark_default",  # defined in Airflow connections
        name="LandingJob",
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

    transform_job = SparkSubmitOperator(
        task_id="transform_job",
        application="/data/transform_job.py",  # script path inside Airflow container
        conn_id="spark_default",  # Spark connection in Airflow
        name="TransformJob",
        verbose=True,
        conf={
            # ---- Iceberg + Hive Catalog ----
            "spark.sql.catalog.hive_catalog": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.hive_catalog.catalog-impl": "org.apache.iceberg.hive.HiveCatalog",
            "spark.sql.catalog.hive_catalog.uri": "thrift://hive-metastore:9083",
            "spark.sql.catalog.hive_catalog.warehouse": "s3a://crypto-data-lake/",
            # ---- Default catalog ----
            "spark.sql.defaultCatalog": "hive_catalog",
            # ---- S3 (MinIO) ----
            "spark.hadoop.fs.s3a.access.key": "minioadmin",
            "spark.hadoop.fs.s3a.secret.key": "minioadmin",
            "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            # ---- Iceberg Extensions ----
            "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            "spark.sql.sources.partitionOverwriteMode": "dynamic",
        },
        jars=",".join(
            [
                "/opt/spark-extra-jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar",
                "/opt/spark-extra-jars/hadoop-aws-3.3.4.jar",
                "/opt/spark-extra-jars/aws-java-sdk-bundle-1.12.262.jar",
            ]
        ),
        application_args=["2025-08-01"],  # like passing CLI args after script
        # You can set master/deploy mode here too:
        # conf_overrides={
        #     "spark.master": "spark://spark-master:7077",
        #     "spark.submit.deployMode": "client",  # change to cluster in prod
        # },
    )

    transform_job_pattern_two = SparkSubmitOperator(
        task_id="transform_job_pattern_two",
        application="/data/transform_job_pattern_two.py",  # script path inside Airflow container
        conn_id="spark_default",  # Spark connection in Airflow
        name="TransformJobPatternTwo",
        verbose=True,
        conf={
            # ---- Iceberg + Hive Catalog ----
            "spark.sql.catalog.hive_catalog": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.hive_catalog.catalog-impl": "org.apache.iceberg.hive.HiveCatalog",
            "spark.sql.catalog.hive_catalog.uri": "thrift://hive-metastore:9083",
            "spark.sql.catalog.hive_catalog.warehouse": "s3a://crypto-data-lake/",
            # ---- Default catalog ----
            "spark.sql.defaultCatalog": "hive_catalog",
            # ---- S3 (MinIO) ----
            "spark.hadoop.fs.s3a.access.key": "minioadmin",
            "spark.hadoop.fs.s3a.secret.key": "minioadmin",
            "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            # ---- Iceberg Extensions ----
            "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            "spark.sql.sources.partitionOverwriteMode": "dynamic",
        },
        jars=",".join(
            [
                "/opt/spark-extra-jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar",
                "/opt/spark-extra-jars/hadoop-aws-3.3.4.jar",
                "/opt/spark-extra-jars/aws-java-sdk-bundle-1.12.262.jar",
            ]
        ),
        application_args=["2025-08-01"],  # like passing CLI args after script
        # You can set master/deploy mode here too:
        # conf_overrides={
        #     "spark.master": "spark://spark-master:7077",
        #     "spark.submit.deployMode": "client",  # change to cluster in prod
        # },
    )

    end = EmptyOperator(task_id="end")
    start >> landing_job >> transform_job >> transform_job_pattern_two >> end  # type: ignore
