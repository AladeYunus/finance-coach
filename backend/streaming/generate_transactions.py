import json, random, time, uuid, os
from datetime import datetime, timezone
import boto3

MERCHANTS = [
    "Amazon", "Tesco", "Netflix", "Uber", "Starbucks",
    "Asda", "Apple", "Sainsbury's", "Deliveroo", "JustEat"
]
CATEGORIES = ["groceries", "entertainment", "transport", "subscriptions", "dining"]

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
        "card_last4": str(random.randint(1111, 9999))
    }

def send_to_kinesis(txn, client):
    client.put_record(
        StreamName="finance-stream",
        Data=json.dumps(txn),
        PartitionKey=txn["id"]
    )

if __name__ == "__main__":
    mode = os.getenv("MODE", "print")  # default to print mode
    interval = int(os.getenv("INTERVAL", 2))

    if mode == "kinesis":
        # dummy creds for localstack
        os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
        os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

        kinesis = boto3.client(
            "kinesis",
            endpoint_url="http://localhost:4566",
            region_name="us-east-1"
        )
        print("Sending transactions to Local Kinesis. Ctrl+C to stop.")
        while True:
            txn = fake_transaction()
            send_to_kinesis(txn, kinesis)
            print("Sent:", txn)
            time.sleep(interval)

    else:
        print("Generating fake transactions. Ctrl+C to stop.")
        while True:
            txn = fake_transaction()
            print(json.dumps(txn), flush=True)
            time.sleep(interval)
