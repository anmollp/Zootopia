from pyspark import SparkContext, SparkConf, TaskContext
from pyspark.sql import SparkSession, SQLContext
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import col, from_json, udf, window, approx_count_distinct

spark = SparkSession.builder.master('spark://c240g5-110107.wisc.cloudlab.us:7078').appName('dataPipeline').getOrCreate()

bootstrap_servers = "128.105.144.46:9092,128.105.144.51:9092,128.105.144.45:9092"

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", bootstrap_servers) \
    .option("subscribe", "idigbio, gbif, obis") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()


def save_kingdom_batch(df, epoch_id):
    df.persist()
    df.write.format("csv").save("hdfs://128.105.144.46:9000/kingdom/{}".format(epoch_id + 1))
    df.unpersist()


def save_species_batch(df, epoch_id):
    df.persist()
    df.write.format("csv").save("hdfs://128.105.144.46:9000/species/{}".format(epoch_id + 1))
    df.unpersist()


def get_batch_num():
    return 1 + int(TaskContext.get().getLocalProperty("streaming.sql.batchId"))


batch_id_udf = udf(get_batch_num)

spark.udf.register("get_batch_num", get_batch_num, IntegerType())

cast_df = df.selectExpr("CAST(key AS STRING) as key", "CAST(value AS STRING) as value")
schema = StructType([
    StructField("http://rs.tdwg.org/dwc/terms/kingdom", StringType(), True),
    StructField("http://rs.tdwg.org/dwc/terms/scientificName", StringType(), True)
])
required_df = cast_df.select("key", "value").withColumn("value", from_json(col("value"), schema))
required_df.createOrReplaceTempView("table")
query_df = spark.sql(
    "SELECT key,"
    " value.`http://rs.tdwg.org/dwc/terms/kingdom` AS kingdom,"
    " value.`http://rs.tdwg.org/dwc/terms/scientificName` AS species,"
    " now() as event_timestamp from table")

query_df.createOrReplaceTempView("table1")

kingdom_df = query_df.withWatermark("event_timestamp", "2 minutes").groupBy(window("event_timestamp", "2 minutes"),
                                                                            "key", "kingdom").count().select("key","kingdom","count")
species_df = query_df.withWatermark("event_timestamp", "2 minutes").groupBy("key",window("event_timestamp", "2 minutes")).agg(approx_count_distinct("species").alias("unique_species_count")).select("key", "unique_species_count")
query1 = kingdom_df.writeStream.outputMode("update").foreachBatch(save_kingdom_batch).trigger(
    processingTime="2 minutes").start()
query2 = species_df.writeStream.outputMode("update").foreachBatch(save_species_batch).trigger(
    processingTime="2 minutes").start()

query1.awaitTermination()
query2.awaitTermination()

