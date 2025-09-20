FROM apache/hive:4.0.0

# Switch to root to install packages and write to /opt/hive/lib
USER root

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Download Postgres JDBC driver
RUN curl -fsSL -o /opt/hive/lib/postgresql-42.7.4.jar \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.4/postgresql-42.7.4.jar

# Download Iceberg Hive runtime JAR
RUN curl -fsSL -o /opt/hive/lib/iceberg-hive-runtime-1.6.1.jar \
    https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-hive-runtime/1.6.1/iceberg-hive-runtime-1.6.1.jar

# Download Hadoop AWS JAR
RUN curl -fsSL -o /opt/hive/lib/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar

# Download AWS SDK bundle JAR
RUN curl -fsSL -o /opt/hive/lib/aws-java-sdk-bundle-1.12.262.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

# Verify downloads
RUN ls -l /opt/hive/lib/postgresql-*.jar /opt/hive/lib/iceberg-hive-runtime-*.jar /opt/hive/lib/hadoop-aws-*.jar /opt/hive/lib/aws-java-sdk-bundle-*.jar

# Switch back to Hive's default user (1000)
USER 1000