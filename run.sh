#!/bin/bash

set -eu

# runs the docker container with the correct parameters
# check if parameters are provided
if [ $# -eq 0 ]; then
    echo "No arguments provided. Run with frequency, check https://www.cellmapper.net/arfcn for conversion of ARFCN to
     frequency. Example for arfcn=1016: ./run.sh 933.4M"
    exit 1
fi

# Use sudo if docker is not available to the current user
if ! docker info > /dev/null 2>&1; then
    DOCKER="sudo docker"
else
    DOCKER="docker"
fi

# build the docker image from the Dockerfile
$DOCKER build -t gsm-scanner .

# run the docker image with the correct parameters and remove the container after it is done
# mount directory for output files
$DOCKER run -it --privileged -e "TZ=Europe/Berlin" -v /dev/bus/usb:/dev/bus/usb -v "$(pwd)/output:/output" gsm-scanner "$@"
