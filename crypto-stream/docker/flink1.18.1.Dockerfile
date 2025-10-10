# Use official Flink image as base
FROM flink:1.18.1-scala_2.12-java17

USER root

# Install Java + Python
RUN apt-get update && \
    apt-get install -y \
    openjdk-17-jdk \
    python3.10 python3.10-venv python3.10-dev python3-pip \
    build-essential curl wget && \
    rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    python3 -m pip install --upgrade pip setuptools wheel

# Fix pemja path for ARM64
RUN mkdir -p /opt/java && \
    ln -sf /usr/lib/jvm/java-17-openjdk-arm64 /opt/java/openjdk && \
    ln -sf /usr/lib/jvm/java-17-openjdk-arm64/include /opt/java/openjdk/include

# Environment setup
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=$JAVA_HOME/bin:$PATH
ENV PYTHONPATH=$FLINK_HOME/python

# Install PyFlink and Python deps
RUN pip install --no-cache-dir \
    apache-flink==1.18.1

RUN pip install --no-cache-dir \
    pandas==2.1.4 \
    numpy==1.24.4

USER flink
WORKDIR /opt/flink