import json
import os
import time
import numpy as np
import datetime
import random

from kafka import KafkaProducer
from json import dumps

connecting=True
print("Start Process")
while connecting:
    try:
        print("Start producer Connection")
        producer = KafkaProducer(bootstrap_servers=['kafka0:29092'],value_serializer=lambda x: dumps(x).encode('utf-8'))
        print("Connection realised")
        connecting=False
    except Exception as e: 
        print(e)
        print("Broker not connected: {}".format(e))
        connecting=True
        time.sleep(5)


user_id=os.getenv('USER_ID')
topic_id=os.getenv('TOPIC_ID')
time_lapse=int(os.getenv('TIME_ID'))
time_ini = datetime.datetime.strptime(os.getenv('TIME_NOW'), '%Y-%m-%d %H:%M:%S.%f')

# time_ini = datetime.datetime.now()

# user_id='12345'
# topic_id='topic_test'
# time_lapse=2



def generatedata(maxpow):

    global time_ini

    data={}



    h2sec = 3600

    min2sec = 60


    #######################
    # INTERVAL OF 8 HOURS

    # initial_time = 13*h2sec

    # final_time = 21*h2sec
    #######################

    #######################
    # INTERVAL OF 8 MINUTES FOR TESTING PURPOUSES
    #######################

    delta_min = 16

    initial_time = time_ini.minute * min2sec

    final_time = (time_ini.minute + delta_min) * min2sec

    mean_time = (initial_time+final_time) / 2
    #######################

    time_now= datetime.datetime.now() 

    current_minute_seconds = time_now.minute * 60 + time_now.second

    current_time_seconds = time_now.hour * 3600 + time_now.minute * 60 + time_now.second



    # power_panel = maxpow/(np.cosh((current_minute_seconds-initial_time)*(4/(mean_time-initial_time))-4)**(0.8))*random.uniform(0.98, 1)

    
    power_panel = maxpow/(np.cosh((current_minute_seconds-initial_time)*(delta_min*0.5/(mean_time-initial_time))-delta_min*0.5)**(0.8*(0.8/(delta_min/10))))

    data["Panel_id"]=user_id

    data["power_panel"] = power_panel

    data["current_status"] = 1

    # data["time_data"] = time_now.strftime("%d/%m/%Y, %H:%M:%S")

    data["time_data"] = str(time_now)

    print(data)

    return data

def senddata(maxpow):

    # Coloca el código para enviar los datos a tu sistema de mensajería
    # Utiliza la variable topic id para especificar el topico destino
    
    data = generatedata(maxpow)

    print("Start sending device {} data".format(data["Panel_id"]))
    
    key = str(data["Panel_id"]).encode('utf-8')

    producer.send(topic=topic_id, value=data, key=key)

    producer.flush()

    print("Message for device {} Sent".format(data["Panel_id"]))

    # print(data)



maxpow = 400 * random.uniform(0.8, 1.2)

# maxpow = 400


while True:
    senddata(maxpow)
    time.sleep(time_lapse)
