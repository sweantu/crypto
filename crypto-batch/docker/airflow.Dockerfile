FROM apache/airflow:2.9.3-python3.11

USER root

# Install Java 17 and procps
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk-headless \
    procps \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

# Install PySpark, Spark provider, and extra libs
RUN pip install pyspark==3.5.1 \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.11.txt" \
    && pip install "apache-airflow-providers-apache-spark" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.11.txt" \
    && pip install boto3 minio trino

USER root

# Copy single entrypoint script
COPY airflow.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow
CMD ["bash", "-c", "\
    export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java)))); \
    export PATH=$JAVA_HOME/bin:$PATH; \
    /entrypoint.sh \
    "]