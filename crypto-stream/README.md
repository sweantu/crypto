```python
from pyflink.table import EnvironmentSettings, TableEnvironment

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)

# connect to remote cluster
t_env.get_config().get_configuration().set_string("execution.target", "remote")
t_env.get_config().get_configuration().set_string("remote.execution.jobmanager.address", "jobmanager")
t_env.get_config().get_configuration().set_string("remote.execution.jobmanager.port", "6123")

t_env.execute_sql("""
    CREATE TABLE numbers (
        num INT
    ) WITH (
        'connector' = 'filesystem',
        'path' = '/workspace/output_table.csv',
        'format' = 'csv'
    )
""")

t_env.execute_sql("INSERT INTO numbers VALUES (1), (2), (3)")
```

flink run -m jobmanager:8081 -py /workspace/test_transform_job_pattern_two.py
