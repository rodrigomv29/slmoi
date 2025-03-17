# Change from:
FROM python:3.12-slim

# To:
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
ENV OPENAI_API_KEY LA-d021098ef5fb4795bd48297a85b35aba89e20a82b8d0485e801bf09f79f547d5

# Run ./main.py when the container launches
CMD ["python", "./main.py"]