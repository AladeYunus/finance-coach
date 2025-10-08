import json, random, time, uuid, os
from datetime import datetime, timezone
import boto3
from botocore.config import Config

# ---- Config ----
STREAM_NAME = os.getenv("KINESIS_STREAM", "finance-stream")
KINESIS_ENDPOINT = os.getenv("KINESIS_ENDPOINT", "http://localhost:4566")
REGION = os.getenv("AWS_REGION", "us-east-1")
SLEEP_SECS = float(os.getenv("SLEEP_SECS", "2"))
TXN_COUNT = int(os.getenv("TXN_COUNT", "0"))  # 0 = infinite

MERCHANTS = [
    "Amazon", "Tesco", "Netflix", "Uber", "Starbucks",
    "Asda", "Apple", "Sainsburys", "Deliveroo", "JustEat"
]
CATEGORIES = ["groceries", "entertainment", "transport", "subscriptions", "dining"]

# Kinesis client (LocalStack endpoint)
kinesis = boto3.client(
    "kinesis",
    region_name="us-east-1",
    endpoint_url="http://localhost:4566",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
)


def fake_transaction():
    amount = round(random.uniform(1.0, 150.0), 2)
    merchant = random.choice(MERCHANTS)
    return {
        "id": str(uuid.uuid4()),
        "merchant": merchant,
        "category_hint": random.choice(CATEGORIES),
        "amount": amount,
        "currency": "GBP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": {"country": "GB"},
        "channel": random.choice(["card_present", "online"]),
        "card_last4": f"{random.randint(1111, 9999)}"
    }

def send_to_kinesis(record: dict):
    # PartitionKey can be anything deterministic; use id to spread load.
    kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(record).encode("utf-8"),
        PartitionKey=record["id"]
    )

if __name__ == "__main__":
    print(f"Sending transactions to Kinesis '{STREAM_NAME}' at {KINESIS_ENDPOINT}. Ctrl+C to stop.")
    i = 0
    try:
        while True:
            if TXN_COUNT and i >= TXN_COUNT:
                break
            txn = fake_transaction()
            send_to_kinesis(txn)
            print(json.dumps(txn), flush=True)  # still print to terminal for visibility
            time.sleep(SLEEP_SECS)
            i += 1
    except KeyboardInterrupt:
        print("\nStopped.")