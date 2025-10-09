# Create a topic

docker exec kafka kafka-topics --create \
 --topic test-topic \
 --bootstrap-server localhost:9092 \
 --partitions 1 --replication-factor 1

# Produce a message

docker exec -it kafka kafka-console-producer \
 --topic test-topic --bootstrap-server localhost:9092

# Consume messages

docker exec -it kafka kafka-console-consumer \
 --topic test-topic --from-beginning --bootstrap-server localhost:9092
