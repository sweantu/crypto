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


t_env.execute_sql("DROP TABLE IF EXISTS klines_source")
t_env.execute_sql("""
CREATE TABLE klines_source (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume DOUBLE
) WITH (
    'connector' = 'filesystem',
    'path' = '/workspace/output/klines/ADAUSDT/2025-09-27',
    'format' = 'csv'
)
""")


def round_half_up(x, decimals=2):
    if x is None:
        return None
    factor = 10**decimals
    return float(int(x * factor + 0.5)) / factor


class EMA7Function(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        self.ema_state = runtime_context.get_state(
            ValueStateDescriptor("ema7", Types.DOUBLE())
        )
        self.buffer = []
        self.alpha = 2 / (7 + 1)

    def process_element(self, value, ctx):
        prev_ema = self.ema_state.value()

        if prev_ema is None:
            self.buffer.append(value["close_price"])
            if len(self.buffer) < 7:
                yield Row(**value.as_dict(), ema7=None)
                return
            ema = sum(self.buffer) / len(self.buffer)
            self.buffer.clear()
        else:
            ema = self.alpha * value["close_price"] + (1 - self.alpha) * prev_ema

        self.ema_state.update(ema)
        yield Row(**value.as_dict(), ema7=round_half_up(ema, 4))


klines_stream = t_env.to_data_stream(t_env.from_path("klines_source")).map(
    lambda r: Row(**r.as_dict(), symbol="ADAUSDT")
)
ema7_typeinfo = Types.ROW_NAMED(
    [
        "window_start",
        "window_end",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume",
        "ema7",
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
        Types.STRING(),
    ],
)
ema_stream = klines_stream.key_by(lambda x: x["symbol"]).process(
    EMA7Function(), output_type=ema7_typeinfo
)


t_env.execute_sql("DROP TABLE IF EXISTS ema7_sink")
t_env.execute_sql("""
CREATE TABLE ema7_sink (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume DOUBLE,
    ema7 DOUBLE,
    symbol STRING
) WITH (
    'connector' = 'filesystem',
    'path' = '/workspace/output/ema7',
    'format' = 'csv',
     'csv.null-literal' = ''
)
""")

t_env.create_temporary_view("ema_stream", t_env.from_data_stream(ema_stream))
t_env.execute_sql("INSERT INTO ema7_sink SELECT * FROM ema_stream")
