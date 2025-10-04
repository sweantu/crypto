from pyspark.sql import SparkSession, types

spark = SparkSession.builder.appName("CryptoETL").getOrCreate()  # type: ignore


df_sorted = (
    spark.sql("select * from serving_db.klines")
    .coalesce(1)  # one partition, not shuffle
    .sortWithinPartitions("group_id")
)


schema = types.StructType(
    [
        *df_sorted.schema.fields,  # keep all original fields
        types.StructField("ema7", types.DoubleType(), True),
        types.StructField("ema20", types.DoubleType(), True),
    ]
)


def round_half_up(x, decimals=2):
    if x is None:
        return None
    factor = 10**decimals
    return float(int(x * factor + 0.5)) / factor


def calc_ema(value, state):
    if value is None:
        return None
    prev, buffer, period, k = (
        state["prev"],
        state["buffer"],
        state["period"],
        state["k"],
    )
    if prev is None:
        buffer.append(value)
        if len(buffer) == period:
            ema = sum(buffer) / len(buffer)
        else:
            ema = None
    else:
        ema = (value - prev) * k + prev

    state["prev"] = ema
    return ema


def ema_in_chunks(iterator):
    ema_configs = {
        "ema7": {"period": 7, "k": 2 / (7 + 1), "prev": None, "buffer": []},
        "ema20": {"period": 20, "k": 2 / (20 + 1), "prev": None, "buffer": []},
    }

    for pdf in iterator:
        ema7, ema20 = [], []
        for p in pdf["close_price"]:
            price = float(p)
            e7 = calc_ema(price, ema_configs["ema7"])
            ema7.append(round_half_up(e7, 2) if e7 is not None else None)
            e20 = calc_ema(price, ema_configs["ema20"])
            ema20.append(round_half_up(e20, 2) if e20 is not None else None)

        pdf["ema7"] = ema7
        pdf["ema20"] = ema20
        pdf = pdf[[*pdf.columns[:-2], "ema7", "ema20"]]
        yield pdf


df = df_sorted.mapInPandas(ema_in_chunks, schema)


df.createOrReplaceTempView("temp")


df = spark.sql("""
with cte as (
    select
        *,
        case 
            when ema7 > ema20 then 'uptrend' 
            when ema7 < ema20 then 'downtrend' 
            else NULL 
        end as trend,
        LAG(open_price, 1) over(order by group_id) as open_price_prev,
        LAG(close_price, 1) over(order by group_id) as close_price_prev
    from temp
)
select
    group_id,
    group_date,
    open_time,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    close_time,
    ema7,
    ema20,
    trend,
    case 
        when close_price_prev < open_price_prev
            and close_price > open_price
            and open_price < close_price_prev
            and close_price > open_price_prev
            and trend = 'downtrend'
        then 'bullish engulfing'
        when close_price_prev > open_price_prev
            and close_price < open_price
            and open_price > close_price_prev
            and close_price < open_price_prev
            and trend = 'uptrend'
        then 'bearish engulfing'
        else NULL
    end as pattern
from cte
""")


df.writeTo("serving_db.pattern_two").tableProperty(
    "format-version", "2"
).createOrReplace()
