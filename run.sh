#!/bin/bash

set -eu

FREQUENCY=${1:-}
# runs the docker container with the correct parameters
# check if parameters are provided
if [ $# -eq 0 ]; then
    echo "No arguments provided. GSM-Monitor will search for GSM signals in the 900MHz band."
    echo "To run with specific frequency/arfcn, check https://www.cellmapper.net/arfcn for 
    conversion of ARFCN to frequency. Example for arfcn=1016: ./run.sh 933.4M"
fi

# Use sudo if docker is not available to the current user
if ! docker info > /dev/null 2>&1; then
    DOCKER="sudo docker"
else
    DOCKER="docker"
fi

# build the docker image from the Dockerfile
echo "Building docker image..."
$DOCKER build -t gsm-monitor .

# run the docker image with the correct parameters and remove the container after it is done
# mount directory for output files
echo "Running docker image..."
$DOCKER run -it --privileged \
  -v /etc/timezone:/etc/timezone:ro \
  -v /etc/localtime:/etc/localtime:ro \
  -v /dev/bus/usb:/dev/bus/usb \
  -v "/home/$USER/output:/output" \
  gsm-monitor "$@"
