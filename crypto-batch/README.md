Hive Metastore
```sql
select * from "DBS";
select * from "TBLS";
select * from "TABLE_PARAMS" where "TBL_ID" = 1;
```
Trino
Grafana:
    Supported via Grafana Plotly panel or Financial charts plugins.
    Zoom, pan, tooltip, crosshair, multiple overlays, annotations.
ClickHouse or InfluxDB

3. Using smaller group keys

If possible, instead of one giant group (100M rows), break it into sub-groups (e.g., (symbol, year) or (symbol, month)), compute EMA in chunks, then stitch together by carrying the last EMA of one partition into the next.
This reduces executor memory pressure further.

1. Using mapInPandas with carry-over
	•	Spark will feed you batches (partitions) instead of whole groups.
	•	You calculate EMA per batch, keep the last EMA, and pass it forward to the next batch.

```python
def ema_in_chunks(iterator):
    alpha = 2 / (7 + 1)
    prev = None
    for pdf in iterator:  # pdf is a chunk of the group
        pdf = pdf.sort_values("timestamp")
        ema = []
        for price in pdf["price"]:
            if prev is None:
                prev = price
            else:
                prev = alpha * price + (1 - alpha) * prev
            ema.append(prev)
        pdf["ema7"] = ema
        yield pdf

ema_df = df.mapInPandas(ema_in_chunks, schema=df.schema.add("ema7", "double"))
```

✅ Works in batch mode
✅ Doesn’t blow up memory
⚠️ Requires sorted input by timestamp within each group (Spark won’t guarantee ordering by default → you need repartition + sort).
Spark doesn’t guarantee ordering inside a partition, even if you sort globally.
For recursive EMA, you must ensure each group (symbol) is sorted by (timestamp) before you feed it into mapInPandas.
1. Sort within groups (symbol, timestamp)

You want all rows of a group together and ordered by time:
```python
from pyspark.sql import functions as F

# 1. Repartition by symbol (ensures all rows of a symbol go to the same set of partitions)
# 2. Sort within partition by timestamp
df_sorted = (
    spark.sql("SELECT * FROM serving_db.sma7")
    .repartition("symbol")   # group rows of the same symbol together
    .sortWithinPartitions("timestamp")  # order rows inside each partition
)
```
	•	repartition("symbol") → ensures grouping by symbol.
	•	sortWithinPartitions("timestamp") → sorts chronologically within each partition.
	•	This avoids expensive global shuffle (orderBy) across the whole dataset.
2. Use mapInPandas with sorted chunks

Now you can safely run chunked EMA:
```python
import pandas as pd
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType

schema = df_sorted.schema.add("ema7", DoubleType())

def ema_in_chunks(iterator):
    alpha = 2 / (7 + 1)  # EMA7
    prev = None
    for pdf in iterator:  # each partition
        pdf = pdf.sort_values("timestamp")  # safety check (local sort)
        ema = []
        for price in pdf["price"]:
            if prev is None:
                prev = price  # or initialize with SMA7 if you prefer
            else:
                prev = alpha * price + (1 - alpha) * prev
            ema.append(prev)
        pdf["ema7"] = ema
        yield pdf

ema_df = df_sorted.mapInPandas(ema_in_chunks, schema)
3. Why this works
	•	Repartition by symbol ensures all rows for a symbol are processed together.
	•	sortWithinPartitions ensures order inside each partition.
	•	mapInPandas lets you iterate partition by partition, carry forward EMA, and never hold the full 100M rows in memory.
⚡ This setup will:
	•	Scale to 100M+ rows per group (no OOM).
	•	Keep memory usage bounded (only chunk at a time).
	•	Run distributed across symbols.
```

```bash
URL="spark://spark-master:7077"
spark-submit \
    --master=${URL} \
    --jars /opt/spark-extra-jars/hadoop-aws-3.3.4.jar,/opt/spark-extra-jars/aws-java-sdk-bundle-1.12.262.jar \
    --conf spark.hadoop.fs.s3a.access.key=minioadmin \
    --conf spark.hadoop.fs.s3a.secret.key=minioadmin \
    --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
    --conf spark.hadoop.fs.s3a.path.style.access=true \
    landing_job.py
pip freeze | xargs pip uninstall -y
```