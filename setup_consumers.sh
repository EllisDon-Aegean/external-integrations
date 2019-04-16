#!/bin/bash

docker-machine create --driver virtualbox --virtualbox-memory 2048 compass-integration 
eval $(docker-machine env compass-integration)
export DOCKER_MACHINE_IP=$(docker-machine ip compass-integration)
docker-compose up -d
