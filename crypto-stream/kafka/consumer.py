from confluent_kafka import Consumer

conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "my-group",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(conf)
consumer.subscribe(["my_topic"])

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"❌ {msg.error()}")
        continue
    print(f"✅ Received: {msg.value().decode('utf-8')} (key={msg.key()})")
