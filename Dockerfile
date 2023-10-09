# based on tutorials at urls listed below
# https://cloud.google.com/run/docs/quickstarts/build-and-deploy/python

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
# sets work directory as /app This also runs as root, maybe we can change that?
RUN useradd -ms /bin/bash web
USER web
WORKDIR /home/web
ENV PATH="/home/web/.local/bin:${PATH}"
COPY --chown=web:web ./reminder .

# Install production dependencies.
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app