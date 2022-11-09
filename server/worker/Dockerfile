# Use an official Python runtime as a parent image
FROM python:slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

COPY worker/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Run app.py when the container launches
ENTRYPOINT ["python", "worker/worker.py"]
