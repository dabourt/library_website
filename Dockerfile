# Use the official Python image from the Docker Hub
FROM python:3.10-alpine

# Set the working directory in the container
WORKDIR /app_lib_web

# Copy the current directory contents into the container at /app_lib_web
COPY . /app_lib_web

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]