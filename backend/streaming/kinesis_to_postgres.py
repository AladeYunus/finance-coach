#!/usr/bin/env python3
"""
Reads fake transactions from LocalStack Kinesis ("finance-stream")
and inserts them into your Docker Postgres database.
"""

import base64
import json
import os
import time

import boto3
import psycopg
from botocore.config import Config


# --- AWS LocalStack (Kinesis) config ---
STREAM_NAME = os.getenv("KINESIS_STREAM", "finance-stream")
KINESIS_ENDPOINT = os.getenv("KINESIS_ENDPOINT", "http://localhost:4566")
REGION = os.getenv("AWS_REGION", "us-east-1")

kinesis = boto3.client(
    "kinesis",
    endpoint_url=KINESIS_ENDPOINT,
    region_name=REGION,
    config=Config(retries={"max_attempts": 3, "mode": "standard"})
)

# --- Docker Postgres config ---
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB   = os.getenv("PG_DB", "finance")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASS = os.getenv("PG_PASS", "postgres")

# --- SQL for inserting data ---
INSERT_SQL = """
INSERT INTO transactions (
  id, merchant, category_hint, amount, currency, ts,
  location_country, channel, card_last4, raw
) VALUES (
  %(id)s, %(merchant)s, %(category_hint)s, %(amount)s, %(currency)s, %(ts)s,
  %(location_country)s, %(channel)s, %(card_last4)s, %(raw)s
)
ON CONFLICT (id) DO NOTHING;
"""

def get_records():
    """Continuously read records from the Kinesis stream and insert into Postgres."""
    # Connect to Postgres (Docker)
    conn = psycopg.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB,
        user=PG_USER, password=PG_PASS
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Get shard iterator
    desc = kinesis.describe_stream(StreamName=STREAM_NAME)
    shard_id = desc["StreamDescription"]["Shards"][0]["ShardId"]
    shard_it = kinesis.get_shard_iterator(
        StreamName=STREAM_NAME,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON"
    )["ShardIterator"]

    print(f"Listening on Kinesis stream '{STREAM_NAME}' ...")

    try:
        while True:
            resp = kinesis.get_records(ShardIterator=shard_it, Limit=100)
            shard_it = resp["NextShardIterator"]

            for r in resp.get("Records", []):
                raw_data = r["Data"]

                # Try to base64-decode; if that fails or doesn't look like JSON, treat as plain text
                try:
                    decoded = base64.b64decode(raw_data).decode("utf-8")
                    if not decoded.strip().startswith("{"):
                        decoded = raw_data.decode("utf-8") if isinstance(raw_data, bytes) else raw_data
                except Exception:
                    decoded = raw_data.decode("utf-8") if isinstance(raw_data, bytes) else raw_data

                data = json.loads(decoded)

                row = {
                    "id": data["id"],
                    "merchant": data["merchant"],
                    "category_hint": data.get("category_hint"),
                    "amount": data["amount"],
                    "currency": data["currency"],
                    "ts": data["timestamp"],
                    "location_country": (data.get("location") or {}).get("country"),
                    "channel": data["channel"],
                    "card_last4": data["card_last4"],
                    "raw": json.dumps(data)
                }
                cur.execute(INSERT_SQL, row)
                print(f"Inserted → {row['merchant']:10s} £{row['amount']:>6}")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    get_records()

