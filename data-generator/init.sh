#/bin/bash

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi solar_main
docker build -t solar_main:latest .
