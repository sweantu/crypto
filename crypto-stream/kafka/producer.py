import csv
import json

from confluent_kafka import Producer

conf = {"bootstrap.servers": "localhost:29092"}
producer = Producer(conf)
topic = "aggtrades-topic"


def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(
            f"✅ Delivered to {msg.topic()} [{msg.partition()}] offset {msg.offset()}"
        )


class AggTrade:
    def __init__(self, row: list[str]) -> None:
        self.agg_trade_id = int(row[0])
        self.price = float(row[1])
        self.quantity = float(row[2])
        self.first_trade_id = int(row[3])
        self.last_trade_id = int(row[4])
        self.ts_int = int(row[5])
        self.is_buyer_maker = row[6].strip().lower() == "true"
        self.is_best_match = row[7].strip().lower() == "true"


with open(
    "../jupyter/workspace/ADAUSDT-aggTrades-2025-09-27.csv",
    newline="",
    encoding="utf-8",
) as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, 1):
        try:
            msg = json.dumps(AggTrade(row).__dict__)
            producer.produce(topic, value=msg.encode("utf-8"), callback=delivery_report)
            if i % 1000 == 0:
                producer.poll(0)
                print(f"Produced {i} messages so far...")
        except Exception as e:
            print(f"❌ Exception while producing message: {i}, error: {e}")

producer.flush()
print("All messages have been produced.")
