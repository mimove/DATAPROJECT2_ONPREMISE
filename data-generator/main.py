import docker
import sys, getopt
import time
import os
import uuid
import random
import datetime

from kafka import KafkaProducer
from json import dumps
# from dotenv import load_dotenv



connecting=True
print("Start Process")
while connecting:
    try:
        print("Start producer Connection")
        producer = KafkaProducer(bootstrap_servers=['kafka:29092'],value_serializer=lambda x: dumps(x).encode('utf-8'))
        print("Connection realised")
        connecting=False
    except Exception as e: 
        print(e)
        print("Broker not connected: {}".format(e))
        connecting=True
        time.sleep(5)


print("#############################")
print("Starting Generator execution")
print("#############################")

# load_dotenv()


topcontainers = 0
elapsedtime = 0
containername=""
topicname = ""
time_ini = ""

list_ids = []

containers=[]

def getcontainers():
    cmd=f"docker ps | grep -c {containername}"
    stream = os.popen(cmd)
    output = stream.read()
    return int(output)

def genuserid(list_ids):
   #  print('Number of containers: {}'.format(list_ids))

    # Selecting a random id from list_ids as the new container and solar panel
    return random.choice(list_ids)

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
    
   #  print(time_ini)
    userid=genuserid(list_ids)
    list_ids
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

   print(f"Top Containers: {topcontainers}")
   print(f"Elapsed Time: {elapsedtime}")
   print(f"Container name: {containername}")
   print(f"Topic name: {topicname}")

   #### MIMOVE CODE ######

   # Creating a list of limited IDs for the solar panels
   
   for i in range(topcontainers):
      list_ids.append(uuid.uuid4().hex)

if __name__ == "__main__":
   main()


time_ini = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


while True:
   numcon=getcontainers()
   print(f"Currently running containers: {len(containers)}")

   for i in list_ids:
      data = {}

      time_now = datetime.datetime.now() 

      data["Panel_id"]=str(i)

      data["power_panel"] = str(0)

      data["current_status"] = str(0)

      # data["time_data"] = time_now.strftime("%d/%m/%Y, %H:%M:%S")

      data["time_data"] = str(time_now)


      print("Start sending device {} data".format(i))
      
      producer.send(topic=topicname, value=data)

      producer.flush()

      print("Message for device {} Sent".format(i))

      # print(data)

   if int(numcon)<int(topcontainers):
      create=random.randint(0,topcontainers-numcon)

      print(f"Containers to be created: {create}")
      for i in range(0,create):
         ##### MIMOVE
         # Ading userid as output to avoid creating a container with the same name as another container that it's running
         [output, userid] = createcontainer()
         list_ids.remove(userid)
      if create == 0:
         print("No containers created this time") 
   else:
      print("No more containers can be created")

   time.sleep(2)

   probab = int(os.environ['PROBABILIDAD'])

   for item in containers:
      prob=random.randint(0, 100/probab)
      if prob == 0:
         # 10% probabilidad de eliminar container
         deletecontainer(item)

         #### MIMOVE #####
         # Adding userid back to the list
         list_ids.append(item)
   
         
   time.sleep(1)



