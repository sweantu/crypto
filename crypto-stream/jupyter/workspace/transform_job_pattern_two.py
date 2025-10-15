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

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
t_env = StreamTableEnvironment.create(env, environment_settings=settings)

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
  ts AS TO_TIMESTAMP_LTZ(ts_int / 1000, 3),
  WATERMARK FOR ts AS ts - INTERVAL '5' MINUTES
) with (
    'connector' = 'filesystem',
    'path' = '/workspace/ADAUSDT-aggTrades-2025-09-27.csv',
    'format' = 'csv'
)
""")


t_env.execute_sql("DROP TEMPORARY VIEW IF EXISTS klines_view")
t_env.execute_sql("""
CREATE TEMPORARY VIEW klines_view AS
SELECT
    window_start,
    window_end,
    ROUND(FIRST_VALUE(price), 4) AS open_price,
    ROUND(MAX(price), 4) AS high_price,
    ROUND(MIN(price), 4) AS low_price,
    ROUND(LAST_VALUE(price), 4) AS close_price,
    ROUND(SUM(quantity), 1) AS volume,
    'ADAUSDT' AS symbol
FROM TABLE(
    TUMBLE(TABLE aggtrades_source, DESCRIPTOR(ts), INTERVAL '15' MINUTES)
)
GROUP BY window_start, window_end
""")

t_env.execute_sql("DROP TABLE IF EXISTS klines")
t_env.execute_sql("""
create table klines (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume DOUBLE,
    symbol STRING
) with (
    'connector' = 'filesystem',
    'path' = '/workspace/output/klines/ADAUSDT/2025-09-27',
    'format' = 'csv'
)
""")


t_env.execute_sql("DROP TABLE IF EXISTS engulfing")
t_env.execute_sql("""
CREATE TABLE engulfing (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume DOUBLE,
    ema7 DOUBLE,
    ema20 DOUBLE,
    trend STRING,
    engulfing_pattern STRING,
    symbol STRING
) WITH (
    'connector' = 'filesystem',
    'path' = '/workspace/output/engulfing',
    'format' = 'csv',
    'csv.null-literal' = ''
)
""")


def round_half_up(x, decimals=2):
    if x is None:
        return None
    factor = 10**decimals
    return float(int(x * factor + 0.5)) / factor


# --- ProcessFunction ---
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
        else:
            return None

    def detect_engulfing(self, current, previous, trend):
        if not previous or not trend:
            return None
        open_price_prev = previous["open_price"]
        close_price_prev = previous["close_price"]
        open_price = current["open_price"]
        close_price = current["close_price"]

        if (
            close_price_prev < open_price_prev
            and close_price > open_price
            and open_price < close_price_prev
            and close_price > open_price_prev
            and trend == "downtrend"
        ):
            return "bullish engulfing"

        if (
            close_price_prev > open_price_prev
            and close_price < open_price
            and open_price > close_price_prev
            and close_price < open_price_prev
            and trend == "uptrend"
        ):
            return "bearish engulfing"

        return None

    def process_element(self, value, ctx):
        prev_row_bytes = self.prev_row_state.value()
        prev_row_state = pickle.loads(prev_row_bytes) if prev_row_bytes else {}
        buffer7_state = copy.deepcopy(prev_row_state.get("buffer7_state", []))
        buffer20_state = copy.deepcopy(prev_row_state.get("buffer20_state", []))

        ema7 = self.calc_ema(
            value["close_price"], 7, prev_row_state.get("ema7"), buffer7_state
        )
        ema20 = self.calc_ema(
            value["close_price"], 20, prev_row_state.get("ema20"), buffer20_state
        )

        trend = self.detect_trend(ema7, ema20)
        pattern = self.detect_engulfing(value.as_dict(), prev_row_state, trend)

        new_state = {
            **value.as_dict(),
            "ema7": ema7,
            "ema20": ema20,
            "trend": trend,
            "pattern": pattern,
            "buffer7_state": buffer7_state,
            "buffer20_state": buffer20_state,
        }
        self.prev_row_state.update(pickle.dumps(new_state))

        yield Row(
            **value.as_dict(),
            ema7=round_half_up(ema7, 4) if ema7 else None,
            ema20=round_half_up(ema20, 4) if ema20 else None,
            trend=trend,
            engulfing_pattern=pattern,
        )


typeinfo = Types.ROW_NAMED(
    [
        "window_start",
        "window_end",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume",
        "ema7",
        "ema20",
        "trend",
        "engulfing_pattern",
        "symbol",
    ],
    [
        Types.SQL_TIMESTAMP(),
        Types.SQL_TIMESTAMP(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.DOUBLE(),
        Types.STRING(),
        Types.STRING(),
        Types.STRING(),
    ],
)


klines_stream = t_env.to_data_stream(t_env.from_path("klines_view"))
engulfing_stream = klines_stream.key_by(lambda x: x["symbol"]).process(
    EngulfingPatternFunction(), output_type=typeinfo
)
t_env.drop_temporary_view("engulfing_view")
t_env.create_temporary_view("engulfing_view", t_env.from_data_stream(engulfing_stream))

statement_set = t_env.create_statement_set()
statement_set.add_insert_sql("INSERT INTO klines SELECT * FROM klines_view")
statement_set.add_insert_sql("INSERT INTO engulfing SELECT * FROM engulfing_view")
statement_set.execute().wait()
