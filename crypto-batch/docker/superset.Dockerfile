# Dockerfile
FROM apache/superset:3.1.0

# Install Trino driver
USER root
RUN pip install --no-cache-dir trino

USER superset