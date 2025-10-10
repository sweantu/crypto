FROM crypto-stream-flink AS flink-base

FROM ubuntu:22.04

USER root

COPY --from=flink-base /opt/flink /opt/flink

ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.11, pip, Java 17, and system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    python3.11 python3.11-venv python3.11-dev python3.11-distutils \
    curl wget git build-essential libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Make Python 3.11 the default for python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 2 \
    && update-alternatives --set python /usr/bin/python3.11

# Fix pemja path for ARM64
RUN mkdir -p /opt/java && \
    ln -sf /usr/lib/jvm/java-11-openjdk-arm64 /opt/java/openjdk && \
    ln -sf /usr/lib/jvm/java-11-openjdk-arm64/include /opt/java/openjdk/include

# Upgrade pip
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python

ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=$JAVA_HOME/bin:$PATH
ENV FLINK_HOME=/opt/flink
ENV PATH=$FLINK_HOME/bin:$PATH
ENV PYTHONPATH=$FLINK_HOME/python

RUN pip install --no-cache-dir \
    apache-flink==1.20.2

RUN pip install --no-cache-dir \
    jupyterlab \
    pandas \
    sqlalchemy \
    psycopg2-binary \
    pyarrow==15.0.2

WORKDIR /workspace
EXPOSE 8888

# Start Jupyter Lab with dynamic JAVA_HOME detection
CMD ["bash", "-c", "\
    jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
    "]