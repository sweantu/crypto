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
        'path' = '/opt/flink/output_table.csv',
        'format' = 'csv'
    )
""")

t_env.execute_sql("INSERT INTO numbers VALUES (1), (2), (3)")
```

flink run -py test_job.py -m jobmanager:8081
