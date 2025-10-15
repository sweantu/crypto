import json

from confluent_kafka import Consumer, KafkaException

conf = {
    "bootstrap.servers": "localhost:29092",
    "group.id": "test-group",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(conf)
topic = "engulfings-topic"
consumer.subscribe([topic])

print("👂 Listening for messages...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        data = json.loads(msg.value().decode("utf-8"))
        print(
            f"📩 Received from topic '{msg.topic()}' "
            f"partition {msg.partition()} "
            f"offset {msg.offset()}:\n{data}\n"
        )
except KeyboardInterrupt:
    pass
finally:
    consumer.close()