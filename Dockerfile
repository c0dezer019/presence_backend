# Use an official Python runtime as a parent image
FROM python:3.10.12-slim

# Set the working directory to /app
WORKDIR /app

# Copy Pipfile and Pipfile.lock to the container
COPY Pipfile Pipfile.lock /app/

# Install pipenv and dependencies
RUN pip install pipenv && \
    pipenv install --deploy --ignore-pipfile

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV MODULE_NAME="asgi"
ENV VARIABLE_NAME="create_asgi"

CMD ["pipenv", "run", "uvicorn", "--factory", "--host", "0.0.0.0", "--port", "8002", "${MODULE_NAME}:${VARIABLE_NAME}"]