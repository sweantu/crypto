FROM trinodb/trino:443

COPY trino/etc/config.properties /etc/trino/config.properties
COPY trino/etc/jvm.config /etc/trino/jvm.config
COPY trino/etc/catalog/iceberg.properties /etc/trino/catalog/iceberg.properties