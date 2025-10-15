# Use official Flink image as base
FROM flink:1.20.2

USER root

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

# Upgrade pip for python
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python

# Environment setup
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=$JAVA_HOME/bin:$PATH
ENV PYTHONPATH=$FLINK_HOME/python

# # Install PyFlink and Python deps
RUN pip install --no-cache-dir \
    apache-flink==1.20.2

RUN pip install --no-cache-dir \
    pandas \
    numpy

WORKDIR $FLINK_HOME/lib

# Kafka SQL connector (compatible with Flink 1.20)
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.20/flink-sql-connector-kafka-3.3.0-1.20.jar

# JDBC connector (shaded) for Flink 1.20
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.3.0-1.20/flink-connector-jdbc-3.3.0-1.20.jar

# PostgreSQL JDBC driver
RUN wget https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar

# ClickHouse driver
RUN wget https://repo1.maven.org/maven2/name/nkonev/flink/flink-sql-connector-clickhouse/1.17.1-8/flink-sql-connector-clickhouse-1.17.1-8.jar

WORKDIR /opt/flink