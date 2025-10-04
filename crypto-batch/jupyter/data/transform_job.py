from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("CryptoETL").getOrCreate()  # type: ignore

bucket = "crypto-data-lake"
output_path = f"s3a://{bucket}/landing_zone/spot/daily/aggTrades/BTCUSDT/2025_08_01"
df = spark.read.parquet(output_path)

df = (
    df.withColumn("timestamp_date", F.from_unixtime(F.col("timestamp") / 1_000_000))
    .withColumn("timestamp_second", (F.col("timestamp") / 1_000_000).cast("long"))
    .withColumn("group_id", (F.col("timestamp_second") / 900).cast("long"))
    .withColumn("group_date", F.from_unixtime(F.col("group_id") * 900))
    .withColumn("transform_date", F.current_date())
    .withColumn("transform_timestamp", F.current_timestamp())
)


spark.sql("""
CREATE DATABASE IF NOT EXISTS transform_db
LOCATION 's3a://crypto-data-lake/transform_zone/'
""")


df.writeTo("transform_db.aggtrades").tableProperty(
    "format-version", "2"
).createOrReplace()


df_kline = spark.sql("""
select 
    group_id,
    group_date,
    first(timestamp, true) as open_time,
    round(first(price, true), 2) as open_price,
    round(max(price), 2) as high_price,
    round(min(price), 2) as low_price,
    round(last(price, true), 2) as close_price,
    round(sum(quantity), 2) as volume,
    last(timestamp, true) as close_time
from transform_db.aggtrades
group by group_id, group_date
order by group_id
""")


spark.sql("""
CREATE DATABASE IF NOT EXISTS serving_db
LOCATION 's3a://crypto-data-lake/serving_zone/'
""")


df_kline.writeTo("serving_db.klines").tableProperty(
    "format-version", "2"
).createOrReplace()
