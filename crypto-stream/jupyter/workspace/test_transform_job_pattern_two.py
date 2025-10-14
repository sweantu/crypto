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


input_stream = t_env.to_data_stream(t_env.from_path("klines_source")).map(
    lambda r: Row("ADAUSDT", int(r[0].timestamp()), float(r[5])),
    output_type=Types.ROW([Types.STRING(), Types.INT(), Types.DOUBLE()]),
)


class EMA7Function(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        self.ema_state = runtime_context.get_state(
            ValueStateDescriptor("ema7", Types.DOUBLE())
        )
        self.buffer = []
        self.alpha = 2 / (7 + 1)

    def process_element(self, value, ctx):
        symbol, ts, close_price = value
        prev_ema = self.ema_state.value()

        if prev_ema is None:
            self.buffer.append(close_price)
            if len(self.buffer) < 7:
                return
            ema = sum(self.buffer) / len(self.buffer)
            self.buffer.clear()
        else:
            ema = self.alpha * close_price + (1 - self.alpha) * prev_ema

        self.ema_state.update(ema)
        yield Row(symbol, ts, close_price, ema)


ema_stream = input_stream.key_by(lambda x: x[0]).process(
    EMA7Function(),
    output_type=Types.ROW(
        [Types.STRING(), Types.INT(), Types.DOUBLE(), Types.DOUBLE()]
    ),
)


t_env.execute_sql("DROP TABLE IF EXISTS ema7_sink")
t_env.execute_sql("""
CREATE TABLE ema7_sink (
    symbol STRING,
    ts INT,
    close_price DOUBLE,
    ema7 DOUBLE
) WITH (
    'connector' = 'filesystem',
    'path' = '/workspace/output/ema7',
    'format' = 'csv'
)
""")

t_env.create_temporary_view("ema_stream", t_env.from_data_stream(ema_stream))
t_env.execute_sql("INSERT INTO ema7_sink SELECT * FROM ema_stream")
