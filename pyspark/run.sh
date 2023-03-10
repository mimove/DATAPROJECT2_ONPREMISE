#/bin/bash
docker cp ../env/log4j2.properties dataproject2_onpremise-spark-master-1:/spark/conf/log4j2.properties
docker exec dataproject2_onpremise-spark-master-1 \
/spark/bin/spark-submit \
--master spark://spark-master:7077 \
--jars /opt/spark-apps/mysql-connector-java-8.0.13.jar \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.2 \
--driver-memory 1G \
--executor-memory 1G \
--conf "spark.worker.instances=2" \
/opt/spark-apps/main.py