from pyflink.common import Row, Types
from pyflink.datastream import (
    KeyedProcessFunction,
    RuntimeContext,
    StreamExecutionEnvironment,
)
from pyflink.datastream.state import ListStateDescriptor, ValueStateDescriptor
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


class EMAFunction(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        self.ema7_state = runtime_context.get_state(
            ValueStateDescriptor("ema7", Types.DOUBLE())
        )
        self.ema20_state = runtime_context.get_state(
            ValueStateDescriptor("ema20", Types.DOUBLE())
        )
        self.buffer7_state = runtime_context.get_list_state(
            ListStateDescriptor("buffer7", Types.DOUBLE())
        )
        self.buffer20_state = runtime_context.get_list_state(
            ListStateDescriptor("buffer20", Types.DOUBLE())
        )

    def calc_ema(self, close_price, period, ema_state, buffer_state):
        if close_price is None:
            return None
        k = 2 / (period + 1)
        prev_ema = ema_state.value()
        buffer = list(buffer_state.get())
        if prev_ema is None:
            buffer.append(close_price)
            if len(buffer) == period:
                ema = sum(buffer) / len(buffer)
                buffer.clear()
            else:
                ema = None
        else:
            ema = (close_price - prev_ema) * k + prev_ema

        ema_state.update(ema)
        buffer_state.update(buffer)
        return round_half_up(ema, 4) if ema is not None else None

    def process_element(self, value, ctx):
        ema7 = self.calc_ema(
            value["close_price"], 7, self.ema7_state, self.buffer7_state
        )
        ema20 = self.calc_ema(
            value["close_price"], 20, self.ema20_state, self.buffer20_state
        )
        yield Row(**value.as_dict(), ema7=ema7, ema20=ema20)


klines_stream = t_env.to_data_stream(t_env.from_path("klines_source")).map(
    lambda r: Row(**r.as_dict(), symbol="ADAUSDT")
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
        "symbol",
    ],
    [
        Types.SQL_TIMESTAMP(),  # TIMESTAMP(3)
        Types.SQL_TIMESTAMP(),
        Types.DOUBLE(),
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
    EMAFunction(), output_type=typeinfo
)


t_env.execute_sql("DROP TABLE IF EXISTS ema_sink")
t_env.execute_sql("""
CREATE TABLE ema_sink (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume DOUBLE,
    ema7 DOUBLE,
    ema20 DOUBLE,
    symbol STRING
) WITH (
    'connector' = 'filesystem',
    'path' = '/workspace/output/ema',
    'format' = 'csv',
     'csv.null-literal' = ''
)
""")

t_env.drop_temporary_view("ema_stream")
t_env.create_temporary_view("ema_stream", t_env.from_data_stream(ema_stream))
t_env.execute_sql("INSERT INTO ema_sink SELECT * FROM ema_stream")
