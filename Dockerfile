# Use the official Python image from the Docker Hub
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make the port provided by the PORT environment variable available to the world outside this container
ENV PORT 8080
EXPOSE ${PORT}

# Define environment variables


### this wont show up on github

##bruhhhhhhhhhhhhhhhhh
###brurrrrrrrrrrrr