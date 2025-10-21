import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, window, hour, minute
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression, LinearRegressionModel

# Initialize Spark Session
spark = SparkSession.builder.appName("Task5_FareTrendPrediction_Assignment").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Paths
MODEL_PATH = "models/fare_trend_model_v2"
TRAINING_DATA_PATH = "training-dataset.csv"

# ------------------- MODEL TRAINING (Offline) ------------------- #
if not os.path.exists(MODEL_PATH):
    print(f"\n[Training Phase] Training new model with feature engineering using {TRAINING_DATA_PATH}...")

    hist_df_raw = spark.read.csv(TRAINING_DATA_PATH, header=True, inferSchema=False)
    hist_df_processed = hist_df_raw.withColumn("event_time", col("timestamp").cast(TimestampType())) \
                                   .withColumn("fare_amount", col("fare_amount").cast(DoubleType()))

    # Aggregate into 5-minute windows
    hist_windowed_df = hist_df_processed.groupBy(window(col("event_time"), "5 minutes")) \
                                        .agg(avg("fare_amount").alias("avg_fare"))

    # Feature engineering
    hist_features = hist_windowed_df.withColumn("hour_of_day", hour(col("window.start"))) \
                                    .withColumn("minute_of_hour", minute(col("window.start")))

    # VectorAssembler
    assembler = VectorAssembler(inputCols=["hour_of_day", "minute_of_hour"], outputCol="features")
    train_df = assembler.transform(hist_features)

    # Train Linear Regression model
    lr = LinearRegression(featuresCol="features", labelCol="avg_fare")
    model = lr.fit(train_df)

    # Save model
    model.write().overwrite().save(MODEL_PATH)
    print(f"[Model Saved] -> {MODEL_PATH}")
else:
    print(f"[Model Found] Using existing model at {MODEL_PATH}")

# ------------------- STREAMING INFERENCE ------------------- #
print("\n[Inference Phase] Starting real-time trend prediction stream...")

schema = StructType([
    StructField("trip_id", StringType()),
    StructField("driver_id", IntegerType()),
    StructField("distance_km", DoubleType()),
    StructField("fare_amount", DoubleType()),
    StructField("timestamp", StringType())
])

raw_stream = spark.readStream.format("socket") \
    .option("host", "localhost") \
    .option("port", 9999).load()

parsed_stream = raw_stream.select(from_json(col("value"), schema).alias("data")).select("data.*") \
    .withColumn("event_time", col("timestamp").cast(TimestampType()))

parsed_stream = parsed_stream.withWatermark("event_time", "1 minute")

# Windowed aggregation
windowed_df = parsed_stream.groupBy(window(col("event_time"), "5 minutes", "1 minute")) \
                           .agg(avg("fare_amount").alias("avg_fare"))

# Feature engineering
windowed_features = windowed_df.withColumn("hour_of_day", hour(col("window.start"))) \
                               .withColumn("minute_of_hour", minute(col("window.start")))

# Assemble features
assembler_inference = VectorAssembler(inputCols=["hour_of_day", "minute_of_hour"], outputCol="features")
feature_df = assembler_inference.transform(windowed_features)

# Load pre-trained model
trend_model = LinearRegressionModel.load(MODEL_PATH)

# Make predictions
predictions = trend_model.transform(feature_df)

# Select final columns
output_df = predictions.select(
    col("window.start").alias("window_start"),
    col("window.end").alias("window_end"),
    "avg_fare",
    col("prediction").alias("predicted_next_avg_fare")
)

# Write predictions to console
query = output_df.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
