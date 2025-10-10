FROM crypto-stream-flink AS flink-base

FROM ubuntu:22.04

USER root

COPY --from=flink-base /opt/flink /opt/flink


# Install Java + Python
RUN apt-get update && \
    apt-get install -y \
    openjdk-17-jdk \
    python3.10 python3.10-venv python3.10-dev python3-pip \
    build-essential curl wget && \
    rm -rf /var/lib/apt/lists/*

# Install Zeppelin
ARG ZEPPELIN_VERSION=0.12.0
RUN wget https://archive.apache.org/dist/zeppelin/zeppelin-${ZEPPELIN_VERSION}/zeppelin-${ZEPPELIN_VERSION}-bin-all.tgz && \
    tar xzf zeppelin-${ZEPPELIN_VERSION}-bin-all.tgz -C /opt && \
    mv /opt/zeppelin-${ZEPPELIN_VERSION}-bin-all /opt/zeppelin && \
    rm zeppelin-${ZEPPELIN_VERSION}-bin-all.tgz

# Configure environment
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN mkdir -p /opt/java && \
    ln -sf /usr/lib/jvm/java-17-openjdk-arm64 /opt/java/openjdk && \
    ln -sf /usr/lib/jvm/java-17-openjdk-arm64/include /opt/java/openjdk/include

ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=$JAVA_HOME/bin:$PATH
ENV PYTHONPATH=/opt/flink/python
ENV ZEPPELIN_HOME=/opt/zeppelin


# Install PyFlink + dependencies
RUN python3 -m pip install --no-cache-dir \
    apache-flink==1.18.1

RUN python3 -m pip install --no-cache-dir \
    pandas==2.1.4 \
    numpy==1.24.4

ENV FLINK_HOME=/opt/flink
ENV PATH=$FLINK_HOME/bin:$PATH
RUN ln -s /usr/bin/python3 /usr/bin/python

EXPOSE 8080
WORKDIR /opt/zeppelin
CMD ["bin/zeppelin.sh"]