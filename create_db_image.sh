#!/bin/bash

# Prompt for the version
read -p "Enter the version tag for this build: " VERSION_TAG

# Define the image name
IMAGE_NAME="daboortocker/library_website_db:$VERSION_TAG"
# Check if the Dockerfile exists
# Build the Docker image
docker build -t $IMAGE_NAME db_server

# Push the Docker image to Docker Hub

docker push $IMAGE_NAME
# Check if the push was successful
echo "Docker image $IMAGE_NAME has been built and pushed to Docker Hub."
