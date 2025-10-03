import logging
import os
import time
import zipfile

import requests
from minio import Minio
from pyspark.sql import SparkSession, types
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

script_dir = os.path.dirname(os.path.abspath(__file__))

client = Minio(
    "minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
)
bucket = "crypto-data-lake"
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

spark = SparkSession.builder.appName("LandingZone").getOrCreate()  # type: ignore


def download_file(url, file_name):
    if os.path.exists(file_name):
        logger.info(f"{file_name} exits")
        return
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        logger.info(
            f"Downloaded {file_name} {(os.path.getsize(file_name) / (1024 * 1024)):.2f}MB completed"
        )


def remove_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
        logger.info(f"{file_name} removed")
    else:
        logger.info(f"{file_name} not found")


def extract_file(extract_dir, zip_path):
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)


extract_dir = os.path.join(script_dir, "unzipped_data")
url = "https://data.binance.vision/data/spot/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2025-08-01.zip"
file_name = os.path.join(script_dir, url.split("/")[-1])

start_t = time.time()
download_file(url, file_name)
end_t = time.time()
logger.info(f"Processed in {(end_t - start_t):.3f} seconds")

extract_file(extract_dir, file_name)
csv_file = os.path.join(extract_dir, os.listdir(extract_dir)[0])
logger.info(f"Extracted CSV: {csv_file}")


schema = types.StructType(
    [
        types.StructField("agg_trade_id", types.LongType(), True),
        types.StructField("price", types.DoubleType(), True),
        types.StructField("quantity", types.DoubleType(), True),
        types.StructField("first_trade_id", types.LongType(), True),
        types.StructField("last_trade_id", types.LongType(), True),
        types.StructField("timestamp", types.LongType(), True),
        types.StructField("is_buyer_maker", types.BooleanType(), True),
        types.StructField("is_best_match", types.BooleanType(), True),
    ]
)

df = spark.read.option("header", "false").schema(schema).csv(csv_file)


df = df.withColumn("ingest_date", F.current_date()).withColumn(
    "ingest_timestamp", F.current_timestamp()
)


output_path = f"s3a://{bucket}/landing_zone/spot/daily/aggTrades/BTCUSDT/2025_08_01"
df.write.mode("overwrite").parquet(output_path)
logger.info(f"Parquet written to: {output_path}")
remove_file(csv_file)
remove_file(file_name)
