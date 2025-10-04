from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType

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
    .appName("FinanceCoach-Kinesis-Print")
    .getOrCreate()
)

raw = (spark.readStream
    .format("aws-kinesis")
    .option("kinesis.streamName", "finance-stream")
    .option("kinesis.region", "eu-west-2")                    # must match the stream’s region
    .option("kinesis.endpointUrl", "http://localhost:4566")   # avoid DNS hostnames
    .option("kinesis.endpointSigningRegion", "eu-west-2")     # tell the SDK which region to sign for
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

query = (json_df.writeStream
    .format("console")
    .option("truncate", "false")
    .start()
)

query.awaitTermination()
