#/bin/bash
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker compose down --remove-orphans -v --rmi local
docker volume prune -f
