# Docker Build Network Troubleshooting

## Problem

The Phoenix Docker image failed during the dependency installation step.

The initial build failed at:

```bash
RUN pip install --no-cache-dir -r requirements.txt

with:Network is unreachable

Investigation

The host operating system had working internet connectivity.

Docker runtime networking was also tested:

docker run --rm python:3.12-slim \
  python -c "import urllib.request; print(urllib.request.urlopen('https://pypi.org', timeout=10).status)"docker run --rm python:3.12-slim \

Result:200

Docker bridge networking was enabled and IPv4 forwarding was active.

Test

The image was rebuilt using the host network:docker build --network=host -t phoenix-app:1.0 .

The build completed successfully.

Result

The issue was isolated to the network path used during the Docker build process rather than the application or Docker runtime networking.

For the current Phoenix environment, the build network is configured as:
build:
  network: host

Lesson Learned

Docker build-time networking and container runtime networking are separate concerns.

A container having internet access does not necessarily mean every build environment will have identical network behavior.

