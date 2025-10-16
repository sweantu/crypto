import copy
import pickle

from pyflink.common import Row, Types
from pyflink.datastream import (
    KeyedProcessFunction,
    RuntimeContext,
    StreamExecutionEnvironment,
)
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

# --- 1️⃣ Environment setup ---
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)  # match Kafka partitions
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
t_env = StreamTableEnvironment.create(env, environment_settings=settings)

# --- 2️⃣ Kafka source ---
t_env.execute_sql("DROP TABLE IF EXISTS aggtrades_source")
t_env.execute_sql("""
CREATE TABLE aggtrades_source (
  agg_trade_id BIGINT,
  price DOUBLE,
  quantity DOUBLE,
  first_trade_id BIGINT,
  last_trade_id BIGINT,
  ts_int BIGINT,
  is_buyer_maker BOOLEAN,
  is_best_match BOOLEAN,
  symbol STRING,
  ts AS TO_TIMESTAMP_LTZ(ts_int / 1000, 3),
  WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'aggtrades-topic',
  'properties.bootstrap.servers' = 'kafka:9092',
  'properties.group.id' = 'pyflink_aggtrades_consumer',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json',
  'json.ignore-parse-errors' = 'true'
)
""")

# --- 3️⃣ Klines view ---
t_env.execute_sql("DROP TEMPORARY VIEW IF EXISTS klines_view")
t_env.execute_sql("""
CREATE TEMPORARY VIEW klines_view AS
SELECT
    window_start,
    window_end,
    symbol,
    CAST(window_start AS DATE) AS landing_date,
    ROUND(FIRST_VALUE(price), 4) AS open_price,
    ROUND(MAX(price), 4) AS high_price,
    ROUND(MIN(price), 4) AS low_price,
    ROUND(LAST_VALUE(price), 4) AS close_price,
    ROUND(SUM(quantity), 1) AS volume
FROM TABLE(
    TUMBLE(TABLE aggtrades_source, DESCRIPTOR(ts), INTERVAL '15' MINUTES)
)
GROUP BY window_start, window_end, symbol
""")

# --- 4️⃣ ClickHouse sinks ---
t_env.execute_sql("DROP TABLE IF EXISTS klines")
t_env.execute_sql("""
CREATE TABLE klines (
    window_start TIMESTAMP_LTZ(3),
    window_end TIMESTAMP_LTZ(3),
    symbol STRING,
    landing_date DATE,
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume DOUBLE
) WITH (
    'connector' = 'clickhouse',
    'url' = 'clickhouse://clickhouse:8123',
    'database-name' = 'testdb',
    'table-name' = 'klines',
    'username' = 'default',
    'password' = '123456',
    'sink.batch-size' = '5000',
    'sink.flush-interval' = '2s',
    'sink.max-retries' = '3',
    'sink.ignore-delete' = 'true'
)
""")

t_env.execute_sql("DROP TABLE IF EXISTS engulfing_clickhouse")
t_env.execute_sql("""
CREATE TABLE engulfing_clickhouse (
    window_start TIMESTAMP_LTZ(3),
    window_end TIMESTAMP_LTZ(3),
    symbol STRING,
    landing_date DATE,
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume DOUBLE,
    ema7 DOUBLE,
    ema20 DOUBLE,
    trend STRING,
    engulfing_pattern STRING
) WITH (
    'connector' = 'clickhouse',
    'url' = 'clickhouse://clickhouse:8123',
    'database-name' = 'testdb',
    'table-name' = 'engulfings',
    'username' = 'default',
    'password' = '123456',
    'sink.batch-size' = '5000',
    'sink.flush-interval' = '2s',
    'sink.max-retries' = '3',
    'sink.ignore-delete' = 'true'
)
""")

# --- 5️⃣ Kafka sink for real-time engulfing ---
t_env.execute_sql("DROP TABLE IF EXISTS engulfing_kafka")
t_env.execute_sql("""
CREATE TABLE engulfing_kafka (
    window_start TIMESTAMP_LTZ(3),
    window_end TIMESTAMP_LTZ(3),
    symbol STRING,
    landing_date DATE,
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume DOUBLE,
    ema7 DOUBLE,
    ema20 DOUBLE,
    trend STRING,
    engulfing_pattern STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'engulfings-topic',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json',
    'key.format' = 'raw',
    'key.fields' = 'symbol',
    'json.timestamp-format.standard' = 'ISO-8601'
)
""")


# --- 6️⃣ Utility ---
def round_half_up(x, decimals=2):
    if x is None:
        return None
    factor = 10**decimals
    return float(int(x * factor + 0.5)) / factor


# --- 7️⃣ Engulfing pattern function ---
class EngulfingPatternFunction(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        self.prev_row_state = runtime_context.get_state(
            ValueStateDescriptor("prev_row_state", Types.PICKLED_BYTE_ARRAY())
        )

    def calc_ema(self, close_price, period, ema_state, buffer_state):
        if close_price is None:
            return None
        k = 2 / (period + 1)
        if ema_state is None:
            buffer_state.append(close_price)
            if len(buffer_state) < period:
                return None
            ema = sum(buffer_state) / len(buffer_state)
            buffer_state.clear()
            return ema
        else:
            return (close_price - ema_state) * k + ema_state

    def detect_trend(self, ema7, ema20):
        if ema7 is None or ema20 is None:
            return None
        if ema7 > ema20:
            return "uptrend"
        elif ema7 < ema20:
            return "downtrend"
        return None

    def detect_engulfing(self, current, previous, trend):
        if not previous or not trend:
            return None
        op_prev, cp_prev = previous["open_price"], previous["close_price"]
        op, cp = current["open_price"], current["close_price"]

        if (
            cp_prev < op_prev
            and cp > op
            and op < cp_prev
            and cp > op_prev
            and trend == "downtrend"
        ):
            return "bullish engulfing"
        if (
            cp_prev > op_prev
            and cp < op
            and op > cp_prev
            and cp < op_prev
            and trend == "uptrend"
        ):
            return "bearish engulfing"
        return None

    def process_element(self, value, ctx):
        prev_bytes = self.prev_row_state.value()
        prev_state = pickle.loads(prev_bytes) if prev_bytes else {}
        buf7 = copy.deepcopy(prev_state.get("buffer7_state", []))
        buf20 = copy.deepcopy(prev_state.get("buffer20_state", []))

        ema7 = self.calc_ema(value["close_price"], 7, prev_state.get("ema7"), buf7)
        ema20 = self.calc_ema(value["close_price"], 20, prev_state.get("ema20"), buf20)
        trend = self.detect_trend(ema7, ema20)
        pattern = self.detect_engulfing(value.as_dict(), prev_state, trend)

        new_state = {
            **value.as_dict(),
            "ema7": ema7,
            "ema20": ema20,
            "trend": trend,
            "pattern": pattern,
            "buffer7_state": buf7,
            "buffer20_state": buf20,
        }
        self.prev_row_state.update(pickle.dumps(new_state))

        yield Row(
            **value.as_dict(),
            ema7=round_half_up(ema7, 4) if ema7 else None,
            ema20=round_half_up(ema20, 4) if ema20 else None,
            trend=trend,
            engulfing_pattern=pattern,
        )


# --- 8️⃣ Output type info ---
typeinfo = Types.ROW_NAMED(
    [
        "window_start",
        "window_end",
        "symbol",
        "landing_date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume",
        "ema7",
        "ema20",
        "trend",
        "engulfing_pattern",
    ],
    [
        Types.SQL_TIMESTAMP(),
        Types.SQL_TIMESTAMP(),
        Types.STRING(),
        Types.SQL_DATE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.STRING(),
        Types.STRING(),
    ],
)

# --- 9️⃣ Apply process ---
klines_stream = t_env.to_data_stream(t_env.from_path("klines_view"))
engulfing_stream = klines_stream.key_by(lambda x: x["symbol"]).process(
    EngulfingPatternFunction(), output_type=typeinfo
)
t_env.drop_temporary_view("engulfing_view")
t_env.create_temporary_view("engulfing_view", t_env.from_data_stream(engulfing_stream))

# --- 🔟 Execute sinks ---
statement_set = t_env.create_statement_set()
statement_set.add_insert_sql("INSERT INTO klines SELECT * FROM klines_view")
statement_set.add_insert_sql(
    "INSERT INTO engulfing_clickhouse SELECT * FROM engulfing_view"
)
statement_set.add_insert_sql(
    "INSERT INTO engulfing_kafka SELECT * FROM engulfing_view where engulfing_pattern IS NOT NULL"
)
statement_set.execute().wait()
