import csv
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

from confluent_kafka import Producer


def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        # print(
        #     f"✅ Delivered to {msg.topic()} [{msg.partition()}] offset {msg.offset()}"
        # )
        pass


class AggTrade:
    def __init__(self, row: list[str], symbol: str) -> None:
        self.agg_trade_id = int(row[0])
        self.price = float(row[1])
        self.quantity = float(row[2])
        self.first_trade_id = int(row[3])
        self.last_trade_id = int(row[4])
        self.ts_int = int(row[5])
        self.is_buyer_maker = row[6].strip().lower() == "true"
        self.is_best_match = row[7].strip().lower() == "true"
        self.symbol = symbol

def produce_messages(topic: str, symbol: str, file_path: str, conf: dict) -> None:
    symbol_to_partition = {"ADAUSDT": 0, "BTCUSDT": 1, "ETHUSDT": 2}
    producer = Producer(conf)
    num_lines = int(subprocess.check_output(["wc", "-l", file_path]).split()[0])
    duration_in_seconds = 90
    t_start = time.time()
    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader, 1):
            try:
                msg = json.dumps(AggTrade(row, symbol).__dict__)
                producer.produce(
                    topic,
                    partition=symbol_to_partition[symbol],
                    key=symbol.encode("utf-8"),
                    value=msg.encode("utf-8"),
                    callback=delivery_report,
                )
                if i % int(num_lines / duration_in_seconds) == 0:
                    producer.poll(0)
                    print(
                        f"Produced {i} messages for {symbol} partition {symbol_to_partition[symbol]} so far..."
                    )
                    time.sleep(1)
            except Exception as e:
                print(f"❌ Exception while producing message: {i}, error: {e}")

    producer.flush()
    t_end = time.time()
    print(f"Time taken to produce {num_lines} messages: {t_end - t_start:.2f} seconds")
    print("All messages have been produced.")


if __name__ == "__main__":
    conf = {"bootstrap.servers": "localhost:29092"}
    topic = "aggtrades-topic"
    # symbols = ["ADAUSDT", "BTCUSDT", "ETHUSDT"]
    symbols = ["ADAUSDT"]
    t_start_all = time.time()
    with ThreadPoolExecutor() as executor:
        for i in range(1):
            t_start_round = time.time()
            file_paths = [
                f"../jupyter/workspace/input/{symbol}-aggTrades-2025-09-{26 + i}.csv"
                for symbol in symbols
            ]
            futures = [
                executor.submit(produce_messages, topic, symbol, file_path, conf)
                for symbol, file_path in zip(symbols, file_paths)
            ]
            for future in futures:
                future.result()
            t_end_round = time.time()
            print(
                f"Time taken for round {i + 1}: {t_end_round - t_start_round:.2f} seconds"
            )
            print(f"Completed round {i + 1}/3")
    t_end_all = time.time()
    print(f"Total time taken: {t_end_all - t_start_all:.2f} seconds")
    print("All rounds completed.")