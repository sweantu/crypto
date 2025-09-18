import time

from confluent_kafka import Producer

# Configure producer
conf = {"bootstrap.servers": "localhost:9092"}

producer = Producer(conf)


# Delivery report callback
def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")


while True:
    # Send messages
    for i in range(0, 5):
        producer.produce(
            topic="my_topic",
            key=str(i),
            value=f"hello world {i}",
            callback=delivery_report,
        )

    # Wait for any outstanding messages to be delivered
    producer.flush()
    time.sleep(5)
