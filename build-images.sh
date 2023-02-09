#!/bin/bash

set -e

docker build -t spark-base:latest ./spark-images/base
docker build -t spark-master:latest ./spark-images/spark-master
docker build -t spark-worker:latest ./spark-images/spark-worker
