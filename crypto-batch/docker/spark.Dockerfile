FROM bitnami/spark:3.5.1

USER root
RUN pip install --no-cache-dir pandas pyarrow==15.0.2
USER 1001