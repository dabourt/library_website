#!/bin/bash

# Prompt for the version tag
read -p "Enter the version tag for this build: " VERSION_TAG

# Define the image name
IMAGE_NAME="daboortocker/library_website:$VERSION_TAG"

# Build the Docker image
docker build -t $IMAGE_NAME backend_server

# Push the Docker image to Docker Hub
docker push $IMAGE_NAME

echo "Docker image $IMAGE_NAME has been built and pushed to Docker Hub."
