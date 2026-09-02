# Docker Container Still Using an Older Image

## Problem

While testing the Phoenix Prometheus metrics, new application metrics were added to the Flask application and a new Docker image was built.

However, the expected latency histogram metrics did not appear in the `/metrics` endpoint.

The application appeared to be running successfully, but the newly added code was not visible inside the running container.

## Investigation

The Docker image had been rebuilt successfully.

However, the existing test container had been created before the new image was built.

This meant that the running container was still based on the older image.

Rebuilding an image does not automatically replace or update containers that were created from a previous version of that image.

## Root Cause

Docker images are immutable templates used to create containers.

A running container does not automatically change when an image with the same tag is rebuilt.

The old container therefore continued running the previous application code even though a newer image existed locally.

## Solution

The existing container was stopped and removed.

A new container was then created from the rebuilt image.

For temporary containers, using the `--rm` option also ensured that the container would be automatically removed after it stopped.

After recreating the container, the new application code and Prometheus histogram metrics became available.

## Verification

The `/metrics` endpoint was checked again.

The expected metrics were now present, including:

    phoenix_http_request_duration_seconds_bucket
    phoenix_http_request_duration_seconds_count
    phoenix_http_request_duration_seconds_sum

The request counter metrics were also visible and updated correctly.

## Lesson Learned

A Docker image and a running Docker container are not the same thing.

Rebuilding an image does not update an already-running container.

After rebuilding an image, the container must be recreated if the new image needs to be used.

A useful troubleshooting question is:

    "Am I testing the new image, or am I still running an old container?"
