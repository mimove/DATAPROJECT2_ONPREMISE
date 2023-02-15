import json
import os
import time
import numpy as np
import datetime
import random

from kafka import KafkaProducer
from json import dumps
from datetime import timedelta


# List of available Kafka brokers
brokers = ["kafka0:29092", "kafka1:29093"]
# brokers = ["localhost:9092", "localhost:9093"]


# Connection to both brokers (looping until both brokers are connected)
connecting=True
print("Start Process")
while connecting:
   for broker in brokers:
      try:
         print("Start producer Connection")
         producer = KafkaProducer(bootstrap_servers=[broker],value_serializer=lambda x: dumps(x).encode('utf-8'))
         if producer.bootstrap_connected():
            print("Conectado al broker: {}".format(broker))
         connecting=False
      except Exception as e: 
         print(e)
         print("Brokers {} not found: {}".format(broker,e))
         connecting=True
         time.sleep(5)



#Getting env. variables passed by data-generator main.py
user_id=os.getenv('USER_ID')
topic_id=os.getenv('TOPIC_ID')
time_lapse=int(os.getenv('TIME_ID'))
time_ini = datetime.datetime.strptime(os.getenv('TIME_NOW'), '%Y-%m-%d %H:%M:%S.%f')


# For testing uncomment the following
# time_ini = datetime.datetime.now()
# user_id='12345'
# topic_id='topic_test'
# time_lapse=2



def generatedata(maxpow):

    global time_ini

    data={}

    # Conversion from hours to seconds and minutes to seconds
    h2sec = 3600

    min2sec = 60


    ######################
    #INTERVAL OF N HOURS

    delta_hour = 1
    
    #######################
    # INTERVAL OF N MINUTES FOR TESTING PURPOUSES
    #######################

    delta_min = 0
    
    #Defining initial time from the variables comming from data-generator/main.py
    initial_time = time_ini.hour * h2sec + time_ini.minute * min2sec

    final_time = (time_ini.hour + delta_hour) * h2sec + (time_ini.minute + delta_min) * min2sec

    mean_time = (initial_time + final_time) / 2
    #######################

    time_now= datetime.datetime.now()-timedelta(minutes=0)+timedelta(hours=1)


    current_time_seconds = time_now.hour * h2sec + time_now.minute * min2sec + time_now.second

    # Equation to calculate the instantaneous power, based on the sech(x), which has a similar shape to that of the normal distribution
    power_panel = maxpow/(np.cosh((current_time_seconds-initial_time)*((delta_hour)*0.5/(mean_time-initial_time))-(delta_hour)*0.5)**(30))

    
    #Defining information of each solar panel: ID, power, status=1(active) and timestamp
    data["Panel_id"]=user_id

    data["power_panel"] = power_panel

    data["current_status"] = 1

    data["time_data"] = str(time_now)

    print(data)

    return data

def senddata(maxpow):

    
    data = generatedata(maxpow)

    # Sending key and data to Kafka. The key in this case is the ID of the panel
    print("Start sending device {} data".format(data["Panel_id"]))
    
    key = str(data["Panel_id"]).encode('utf-8')

    producer.send(topic=topic_id, value=data, key=key)

    producer.flush()

    print("Message for device {} Sent".format(data["Panel_id"]))

    print(data)



maxpow = 400 * random.uniform(0.8, 1.2) # Max. power of each solar panel. It can be from -20% to +20% of 400W


while True:
    senddata(maxpow)
    time.sleep(time_lapse)
