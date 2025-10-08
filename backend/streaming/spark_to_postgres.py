from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType

PG_URL = "jdbc:postgresql://localhost:5432/finance"
PG_TABLE = "transactions"
PG_USER = "postgres"
PG_PASS = "postgres"

schema = (StructType()
    .add("id", StringType())
    .add("merchant", StringType())
    .add("category_hint", StringType())
    .add("amount", DoubleType())
    .add("currency", StringType())
    .add("timestamp", StringType())
    .add("channel", StringType())
    .add("card_last4", StringType())
)

spark = (SparkSession.builder
    .appName("FinanceCoach-Kinesis-to-Postgres")
    .config("spark.jars", "jars/postgresql-42.7.8.jar")
    .getOrCreate()
)

raw = (spark.readStream
    .format("aws-kinesis")
    .option("kinesis.streamName", "finance-stream")
    .option("kinesis.region", "us-east-1")                    # must match the stream’s region
    .option("kinesis.endpointUrl", "http://localhost:4566")   # avoid DNS hostnames
    .option("kinesis.endpointSigningRegion", "us-east-1")     # tell the SDK which region to sign for
    .option("kinesis.startingposition", "TRIM_HORIZON")       # or LATEST
    .option("aws.credentials.provider", "STATIC")
    .option("aws.accessKeyId", "test")
    .option("aws.secretKey", "test")
    .load()
)




json_df = (raw
    .selectExpr("CAST(data AS STRING) AS json")
    .select(from_json(col("json"), schema).alias("data"))
    .select("data.*")
)

def write_batch(batch_df, batch_id):
    (batch_df.write
        .format("jdbc")
        .option("url", PG_URL)
        .option("dbtable", PG_TABLE)
        .option("user", PG_USER)
        .option("password", PG_PASS)
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save())

query = (json_df.writeStream
    .foreachBatch(write_batch)
    .start()
)

query.awaitTermination()
