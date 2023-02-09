FROM python:3.9.15-slim

# Esta parte ya sabéis cómo va
RUN mkdir app

WORKDIR /app
RUN mkdir solar_panel
COPY main.py main.py
COPY ./solar_panel/ ./solar_panel/
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Installing docker inside the container
RUN apt update && apt install --yes apt-transport-https ca-certificates curl gnupg2 software-properties-common && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && apt update && apt install --yes docker-ce 

# # Rebuilding the solar_gen image
# WORKDIR /app/solar_panel
# RUN docker rmi solar_gen
# RUN docker build -t solar_gen:latest

# WORKDIR /app

# IF CREATING THE IMAGE DOESN'T WORK YOU SHOULD RUN
# docker system prune --force

CMD [ "python", "-u", "main.py"]