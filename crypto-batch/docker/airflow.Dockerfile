FROM apache/airflow:2.9.3-python3.11

# Switch to root just for file operations
USER root
COPY airflow.sh /opt/airflow/airflow.sh
RUN chmod +x /opt/airflow/airflow.sh

# Switch back to airflow user (default)
USER airflow

ENTRYPOINT ["/opt/airflow/airflow.sh"]