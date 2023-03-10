import time

from pyspark.sql import SparkSession

# Import sql functions
from pyspark.sql.functions import *

from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType


# This function is used to write the microbatches that Spark needs to work in "streaming" sending information to a DataBase like MySQL
def foreach_batch_function(df, epoch_id):
    # This function is used to write data on table panelData which has the raw data of each panel
    df.write.mode("append")\
        .format("jdbc") \
        .option("driver","com.mysql.cj.jdbc.Driver") \
        .option("url", "jdbc:mysql://db:3306/app_db?allowPublicKeyRetrieval=true&useSSL=false") \
        .option("dbtable", "panelData") \
        .option("user", "root") \
        .option("password", "my_secret_password") \
        .save()
    
    pass


def foreach_batch_function_total(df, epoch_id):
    # This function is used to write data on table panelDataAgg, which has the aggregate data of all the panels groupedBy ID and calculation the mean value of 
    # the power in each window
    df.write.mode("append")\
        .format("jdbc") \
        .option("driver","com.mysql.cj.jdbc.Driver") \
        .option("url", "jdbc:mysql://db:3306/app_db?allowPublicKeyRetrieval=true&useSSL=false") \
        .option("dbtable", "panelDataAgg") \
        .option("user", "root") \
        .option("password", "my_secret_password") \
        .save()
    
    pass


# Function to initialize Spark. Some configuration options have been added for increasing the fault tolerance of the system
def init_spark():
    print("Creating session")
    spark = SparkSession.builder \
        .appName("DP2_SOLARPANELS") \
        .config("spark.task.maxFailures", "5") \
        .config("spark.speculation", "true") \
        .config("spark.driver.allowMultipleContexts", "true") \
        .config("spark.dynamicAllocation.enabled", "true") \
        .config("spark.dynamicAllocation.minExecutors", "1") \
        .config("spark.shuffle.service.enabled", "true") \
        .config("spark.executor.instances", "1") \
        .getOrCreate()
    return spark




def main():
    spark=init_spark()


    # Defining spark schema for the topic panelInfo
    schema = StructType([ 
    StructField("Panel_id", StringType(), True),
    StructField("power_panel" , DoubleType(), True),
    StructField("current_status" , IntegerType(), True),
    StructField("time_data" , TimestampType(), True),
    ])


    # List of available Kafka Brokers
    brokers = ["kafka0:29092", "kafka1:29093"]


    # Connection to both brokers (looping until both brokers are connected)
    connecting=True
    print("Start Process")
    while connecting:
        for broker in brokers:
            try:

                # Connecting to kafta to pull messages from the topic panelInfo
                stream_detail_df = spark.readStream.format("kafka")\
                                .option("kafka.bootstrap.servers", broker)\
                                .option("subscribe", "panelInfo")\
                                .option("startingOffsets", "earliest")\
                                .load() \
                                .select(from_json(col("value").cast("string"), schema).alias("parsed_value")) \
                                .select(col("parsed_value.*")).na.fill(value=0)
        
                if stream_detail_df.isStreaming:
                    print("Conectado al broker: {}".format(broker))
                connecting=False
            except Exception as e:
                print("Error al conectar al broker {}: {}".format(broker, e))
                time.sleep(3)



    df_test = stream_detail_df.select('*') # Storing the Raw Values of the topic in a DataFrame to print them in the console
    

    # The following line is used to write the data to the DB. Note how the writeStream method needs to call the method foreachBatch as Spark
    # streaming works with microbatches.
    query = stream_detail_df.writeStream.outputMode("append").foreachBatch(foreach_batch_function).start()

    # Printing raw data in the console
    df_test \
        .writeStream\
        .outputMode('Append')\
        .format('console')\
        .start()

    # The following lines of codes are used to obtained tha aggregation of the mean power, grouped by PowerID every 30 seconds
    # The while loop is used for fault tolerance, so in case a spark-worker stops, the stream of data can be resumed.
    while True:
        try:
            df = stream_detail_df.withColumn("timestamp", stream_detail_df["time_data"])

            # A time watermark is needed by spark to perform the aggregation
            result = df.withWatermark("timestamp", "30 seconds").groupBy(
                window(df["time_data"], "30 seconds"), 
                df["Panel_id"]
            ) \
                .agg(avg("power_panel")).withColumnRenamed("avg(power_panel)", "total_power")
            
            # The new column window (which is a json of its start and end times), is splitted in two columns, and then it's dropped
            result = result \
                .withColumn("window_start", col("window").start) \
                .withColumn("window_end", col("window").end) \
                .drop(col("window"))                                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                                                

            # The aggregation data is written in the panelDataAgg table created in MySQL
            query_2 = result.writeStream.outputMode("update").foreachBatch(foreach_batch_function_total).start()

            # The result of the aggregation is printed on the console for checking purpouses
            result.writeStream \
                .outputMode("update") \
                .format("console") \
                .option("truncate", "false") \
                .option("watermark", "timestamp") \
                .start()

            query_2.awaitTermination()

            break

        except:
            time.sleep(2)


    query.awaitTermination()
          

if __name__ == '__main__':
  main()

