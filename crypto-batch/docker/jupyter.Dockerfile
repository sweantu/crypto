FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.11, pip, Java 17, and system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3.11-distutils \
    openjdk-17-jdk-headless \
    curl wget git build-essential libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Make Python 3.11 the default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 2

# Upgrade pip
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Base packages and PySpark
RUN python3 -m pip install --no-cache-dir \
    pyspark==3.5.1 \
    jupyterlab

# Data packages
RUN python3 -m pip install --no-cache-dir \
    pandas \
    sqlalchemy \
    psycopg2-binary \
    pyarrow==15.0.2

# Cloud / services packages
RUN python3 -m pip install --no-cache-dir \
    boto3 \
    trino \
    minio

# Create Jupyter user
RUN useradd -ms /bin/bash jovyan
USER jovyan
WORKDIR /home/jovyan/work

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter Lab with dynamic JAVA_HOME detection
CMD ["bash", "-c", "\
    export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java)))); \
    export PATH=$JAVA_HOME/bin:$PATH; \
    jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
    "]