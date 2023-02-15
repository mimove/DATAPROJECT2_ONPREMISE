import docker
import sys, getopt
import time
import os
import uuid
import random
import datetime

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


print("#############################")
print("Starting Generator execution")
print("#############################")

# Env. variables initialization

topcontainers = 0
elapsedtime = 0
containername=""
topicname = ""
time_ini = ""

list_ids = []

containers=[]

# Function to get the actual number of solar_panels active
def getcontainers():
    cmd=f"docker ps | grep -c {containername}"
    stream = os.popen(cmd)
    output = stream.read()
    return int(output)


# Selecting a random id from list_ids as the new container and solar panel
def genuserid(list_ids):
    return random.choice(list_ids)


# Function to delete the container
def deletecontainer(container_id):
    cmd=f"docker container rm {container_id} -f "
    stream = os.popen(cmd)
    output = stream.read()
    containers.remove(container_id)
    print(f"Container Removed with id: {container_id}")


def createcontainer():
    global list_ids
    global containername
    global elapsedtime
    global topcontainers
    global containers
    global topicname
    global time_ini
    
    userid=genuserid(list_ids)

    # The following command creates a container for a solar panel, and it passes info about TIME, USER, TOPIC and docker network through env. variables
    cmd=f"docker run --name {userid} -e TIME_ID={elapsedtime} -e USER_ID={userid} -e TOPIC_ID={topicname} -e TIME_NOW='{time_ini}' --network=kafka-spark-mysql -d {containername}:latest"
   #  cmd=f"docker run --name {userid} -e TIME_ID={elapsedtime} -e USER_ID={userid} -e TOPIC_ID={topicname} -e TIME_NOW='{time_ini}' -d {containername}:latest"

    stream = os.popen(cmd)
    output = stream.read().replace("\n","")
    if userid not in containers:
      containers.append(userid)
    print(f"Container Created with id: {output} for user: {userid}")
    return output, userid

def main():
   global containername
   global elapsedtime
   global topcontainers
   global list_ids
   global topicname


   topcontainers = int(os.environ['CONTAINERS'])
   elapsedtime = int(os.environ['TIME'])
   containername = os.environ['IMAGE']
   topicname = os.environ['TOPIC']

   # For testing uncomment the following
   # topcontainers = 1
   # elapsedtime = 5
   # containername="solar_gen_premise"
   # topicname = "panelInfo"
   # # time_ini = ""

   print(f"Top Containers: {topcontainers}")
   print(f"Elapsed Time: {elapsedtime}")
   print(f"Container name: {containername}")
   print(f"Topic name: {topicname}")

   # Creating a list of <topcontainers> IDs for the solar panels
   for i in range(topcontainers):
      list_ids.append(uuid.uuid4().hex)

if __name__ == "__main__":
   main()


time_ini = (datetime.datetime.now()-timedelta(minutes=0)).strftime('%Y-%m-%d %H:%M:%S.%f')


while True:
   numcon=getcontainers()
   print(f"Currently running containers: {len(containers)}")

   for i in list_ids:
      data = {}

      time_now = (datetime.datetime.now()-timedelta(minutes=0)) 

      #Each solar panel has to send status=0 once it's offline, along with its ID and timestamp

      data["Panel_id"]=str(i)

      data["power_panel"] = str(0)

      data["current_status"] = str(0)

      data["time_data"] = str(time_now)

      print("Start sending device {} data".format(i))


      # Sending key and data to Kafka. The key in this case is the ID of the panel
      key = str(i).encode('utf-8')
      producer.send(topic=topicname, value=data, key=key)

      producer.flush()

      print("Message for device {} Sent".format(i))


   if int(numcon)<int(topcontainers):
      create=random.randint(0,topcontainers-numcon)

      print(f"Containers to be created: {create}")
      for i in range(0,create):

         # Ading userid as output to avoid creating a container with the same name as another container that it's running
         [output, userid] = createcontainer()
         list_ids.remove(userid)
      if create == 0:
         print("No containers created this time") 
   else:
      print("No more containers can be created")

   time.sleep(2)

   probab = int(os.environ['PROBABILIDAD']) # Probability that a container stops in a certain moment

   for item in containers:
      prob=random.randint(0, round(100/probab,0))
      if prob == 0:
         deletecontainer(item)

         # Adding userid back to the list so it's available to initialize the container in the future.
         list_ids.append(item)
   
         
   time.sleep(2)




