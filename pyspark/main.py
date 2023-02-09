from pyspark.sql import SparkSession

# Import sql functions
from pyspark.sql.functions import *

from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType



def foreach_batch_function(df, epoch_id):
    # global db_target_properties 


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
    # global db_target_properties 


    df.write.mode("append")\
        .format("jdbc") \
        .option("driver","com.mysql.cj.jdbc.Driver") \
        .option("url", "jdbc:mysql://db:3306/app_db?allowPublicKeyRetrieval=true&useSSL=false") \
        .option("dbtable", "panelDataAgg") \
        .option("user", "root") \
        .option("password", "my_secret_password") \
        .save()
    
    pass



def init_spark():
    print("Creating session")   
    spark = SparkSession.builder.appName("DP2_SOLARPANELS").getOrCreate()
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


    # Connecting to kafta to pull messages from the topic panelInfo
    stream_detail_df = spark.readStream.format("kafka")\
                     .option("kafka.bootstrap.servers", "kafka0:29092")\
                     .option("subscribe", "panelInfo")\
                     .option("startingOffsets", "earliest")\
                     .load() \
                     .select(from_json(col("value").cast("string"), schema).alias("parsed_value")) \
                     .select(col("parsed_value.*")).na.fill(value=0)
     
    df_test = stream_detail_df.select('*')
    
    # df.printSchema()


    query = stream_detail_df.writeStream.outputMode("append").foreachBatch(foreach_batch_function).start()

    # Start running the query that prints the running counts to the console
    # query = df\
    #     .writeStream\
    #     .outputMode('Append')\
    #     .format('console')\
    #     .start()

    # df_test \
    #     .writeStream\
    #     .outputMode('Append')\
    #     .format('console')\
    #     .start()

    
    # Realizar una agregación en batches cada 10 segundos
    
    df = stream_detail_df.withColumn("timestamp", stream_detail_df["time_data"])

    result = df.withWatermark("timestamp", "30 seconds").groupBy(
        window(df["time_data"], "30 seconds", "2 seconds"), 
        df["Panel_id"]
    ) \
        .agg(avg("power_panel")).withColumnRenamed("avg(power_panel)", "total_power")
    

    result = result \
        .withColumn("window_start", col("window").start) \
        .withColumn("window_end", col("window").end) \
        .drop(col("window"))                                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                                                
    # result.show(truncate=False)

    query_2 = result.writeStream.outputMode("update").foreachBatch(foreach_batch_function_total).start()

    result.writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", "false") \
        .option("watermark", "timestamp") \
        .start()


    query.awaitTermination()

    # # Start running the query that prints the running counts to the console
    # query = df\
    #     .writeStream\
    #     .outputMode('Append')\
    #     .format('console')\
    #     .start()


    # query.awaitTermination()
 
                    

if __name__ == '__main__':
  main()

