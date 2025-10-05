import logging
import sys

from pyspark.errors.exceptions.base import AnalysisException
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def table_exists(spark: SparkSession, database: str, table: str) -> bool:
    try:
        spark.catalog.getTable(f"{database}.{table}")
        return True
    except AnalysisException:
        return False


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if len(sys.argv) < 3:
    logger.error("Usage: spark-submit end_transform_job.py <landing_date> <symbol>")
    sys.exit(1)

spark = SparkSession.builder.appName("CryptoETL").getOrCreate()  # type: ignore


bucket = "crypto-data-lake"
landing_date = sys.argv[1]  # comes from {{ ds }}
symbol = sys.argv[2]  # comes from {{ params.symbol }}
output_path = (
    f"s3a://{bucket}/landing_zone/spot/daily/aggTrades/{symbol}/{landing_date}"
)
df = spark.read.parquet(output_path)


df = (
    df.withColumn("timestamp_date", F.from_unixtime(F.col("timestamp") / 1_000_000))
    .withColumn("timestamp_second", (F.col("timestamp") / 1_000_000).cast("long"))
    .withColumn("group_id", (F.col("timestamp_second") / 900).cast("long"))
    .withColumn("group_date", F.from_unixtime(F.col("group_id") * 900))
    .withColumn("transform_date", F.current_date())
    .withColumn("transform_timestamp", F.current_timestamp())
    .withColumn("landing_date", F.to_date(F.lit(landing_date), "yyyy-MM-dd"))
    .withColumn("symbol", F.lit(symbol))
)


spark.sql("""
CREATE DATABASE IF NOT EXISTS transform_db
LOCATION 's3a://crypto-data-lake/transform_zone/'
""")


if table_exists(spark, "transform_db", "aggtrades"):
    df.writeTo("transform_db.aggtrades").overwritePartitions()
    logger.info(
        f"Table transform_db.aggtrades overwritten for {symbol} on {landing_date}"
    )
else:
    df.writeTo("transform_db.aggtrades").tableProperty(
        "format-version", "2"
    ).partitionedBy("symbol", "landing_date").createOrReplace()
    logger.info(f"Table transform_db.aggtrades created for {symbol} on {landing_date}")


spark.sql("""
CREATE DATABASE IF NOT EXISTS serving_db
LOCATION 's3a://crypto-data-lake/serving_zone/'
""")

sql_stmt = f"""
select 
    group_id,
    group_date,
    first(timestamp, true) as open_time,
    round(first(price, true), 2) as open_price,
    round(max(price), 2) as high_price,
    round(min(price), 2) as low_price,
    round(last(price, true), 2) as close_price,
    round(sum(quantity), 2) as volume,
    last(timestamp, true) as close_time,
    landing_date,
    symbol
from transform_db.aggtrades
where landing_date = DATE('{landing_date}') AND symbol = '{symbol}'
group by group_id, group_date, landing_date, symbol
"""
logger.info(f"SQL Statement:\n{sql_stmt}")
df_kline = spark.sql(sql_stmt)


if table_exists(spark, "serving_db", "klines"):
    df_kline.writeTo("serving_db.klines").overwritePartitions()
    logger.info(f"Table serving_db.klines overwritten for {symbol} on {landing_date}")
else:
    df_kline.writeTo("serving_db.klines").tableProperty(
        "format-version", "2"
    ).partitionedBy("symbol", "landing_date").createOrReplace()
    logger.info(f"Table serving_db.klines created for {symbol} on {landing_date}")
