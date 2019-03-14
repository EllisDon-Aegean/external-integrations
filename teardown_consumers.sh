#!/bin/bash

docker-compose down
docker-machine stop compass-integration
docker-machine rm compass-integration -y
