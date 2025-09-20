```bash
mkdir -p extra-jars && \
    wget -P extra-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.6/hadoop-aws-3.3.6.jar && \
    wget -P extra-jars https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.547/aws-java-sdk-bundle-1.12.547.jar && \
    wget -P extra-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.6/hadoop-common-3.3.6.jar && \
    wget -P extra-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-auth/3.3.6/hadoop-auth-3.3.6.jar
```
aws-java-sdk-bundle-1.12.262.jar
hadoop-aws-3.3.4.jar
iceberg-spark-runtime-3.5_2.12-1.6.1.jar