# Use the official Python image from the Docker Hub
FROM python:3.10-alpine

# Set the working directory in the container
WORKDIR /app_lib_web_db

# Copy the current directory contents into the container at /app_lib_web_db
COPY db_app.py /app_lib_web_db/
COPY requirements.txt /app_lib_web_db/
COPY Dockerfile /app_lib_web_db/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary JSON files if they do not exist
RUN mkdir -p /var/lib_db && \
    echo '{"data": []}' > /var/lib_db/books.json && \
    echo '{"data": []}' > /var/lib_db/users.json

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=db_app.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]