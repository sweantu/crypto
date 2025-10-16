#!/bin/bash
# run_clickhouse_init.sh

# Set container name (from docker-compose)
CONTAINER_NAME=clickhouse

# ClickHouse credentials
USER=default
PASSWORD=123456
DATABASE=testdb

# Directory containing SQL scripts
SQL_DIR=./init-scripts

# Run each SQL file in order
for f in $(ls "$SQL_DIR"/*.sql | sort); do
    echo "Running $f..."
    docker compose exec -T $CONTAINER_NAME sh -c "clickhouse-client --user $USER --password $PASSWORD --database $DATABASE" < "$f"
done

docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --create --topic aggtrades-topic --partitions 4 --replication-factor 1
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --create --topic engulfings-topic --partitions 4 --replication-factor 1

echo "All scripts executed!"