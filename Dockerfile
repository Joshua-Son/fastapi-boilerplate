# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for psycopg2
# RUN apt-get update && apt-get install -y \
#     libpq-dev \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy the Pipfile and Pipfile.lock
COPY Pipfile ./

# Install project dependencies
RUN pipenv install --deploy --ignore-pipfile

# Copy the application code and entrypoint script
COPY . .

# Make the prestart script executable
RUN chmod +x prestart.sh entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["bash", "./entrypoint.sh"]


