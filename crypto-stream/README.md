flink run -m jobmanager:8081 -py /workspace/

can find a community ClickHouse connector that is compatible with Flink 1.20 (pre-compiled jar), and give you a direct download link. Do you want me to do that now?
https://mvnrepository.com/artifact/name.nkonev.flink/flink-sql-connector-clickhouse

name.nkonev:flink-sql-connector-clickhouse:1.17.1-8
JAR ~5.4 MB
This one is stable and published.    Newer version “1.17.1-9” is mentioned in the same repository. 
org.apache.flink:flink-connector-jdbc-clickhouse:3.2.0-1.20.0-h0.cbu.mrs.351.r22
Specialized JDBC connector for ClickHouse (Huawei Cloud SDK)
It explicitly advertises support for Flink 1.20.0 in its version name. 
com.clickhouse.flink:connector:0.0.1
Official / minimal stub
It appears on Maven Central under com.clickhouse.flink:connector version 0.0.1.    But as noted earlier, it seems to be a metadata stub (no full compiled classes).

# grafana
SELECT DISTINCT symbol FROM testdb.engulfings ORDER BY symbol

SELECT
    window_start AS time,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    ema7,
    ema20,
    CASE
        WHEN engulfing_pattern IS NOT NULL THEN close_price
        ELSE NULL
    END AS engulfing_close
FROM testdb.engulfings
WHERE
    symbol = '${symbol}'
    AND window_start BETWEEN
        parseDateTimeBestEffortOrNull('${__from:date}')
        AND parseDateTimeBestEffortOrNull('${__to:date}')
ORDER BY window_start ASC;