# Create a topic

docker exec kafka kafka-topics --create \
 --topic test-topic \
 --bootstrap-server localhost:9092 \
 --partitions 1 --replication-factor 1

kafka-topics --bootstrap-server localhost:9092 --create --topic aggtrades-topic --partitions 3 --replication-factor 1

# Produce a message

docker exec -it kafka kafka-console-producer \
 --topic test-topic --bootstrap-server localhost:9092

# Consume messages

docker exec -it kafka kafka-console-consumer \
 --topic test-topic --from-beginning --bootstrap-server localhost:9092


# check partitions
kafka-topics --bootstrap-server localhost:9092 --list
kafka-topics --bootstrap-server localhost:9092 --topic aggtrades-topic --describe

# Consume from partition 0
kafka-console-consumer --bootstrap-server localhost:9092 \
--topic aggtrades-topic --partition 0 --from-beginning --max-messages 5

# Consume from partition 1
kafka-console-consumer --bootstrap-server localhost:9092 \
--topic aggtrades-topic --partition 1 --from-beginning --max-messages 5