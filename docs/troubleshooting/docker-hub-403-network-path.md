# Docker Hub Pull Failed With HTTP 403

## Problem

While adding Grafana Tempo to the Phoenix observability stack, Docker Compose failed while pulling the Tempo image:

    failed to resolve reference "docker.io/grafana/tempo:3.0.2"
    403 Forbidden

The same problem also occurred with a simple Docker Hub image:

    docker pull hello-world

This showed that the failure was not specific to Grafana Tempo.

## Investigation

The Docker daemon was checked for configured proxy variables and none were found.

The shell environment also did not contain an active proxy configuration.

Direct requests to Docker Hub endpoints were tested.

At one point, requests to:

    https://registry-1.docker.io/v2/

returned HTTP 403 instead of the expected authentication challenge.

IPv4 connectivity was also tested separately and the registry endpoint returned the expected HTTP 401 response.

The Docker Hub authentication endpoint was reachable over the working network path.

Docker Hub image pulls still failed until the host network path was changed.

## Root Cause

The failure was related to the network or egress path between the Phoenix VM and Docker Hub.

It was not caused by:

    Grafana Tempo configuration
    Docker Compose syntax
    the requested Tempo image name
    an application-level Phoenix configuration

The exact upstream network cause was not conclusively proven, so the issue should not be documented as an IPv6-specific failure.

## Solution

A VPN connection was enabled, changing the external network path used by the VM.

After the network path changed, Docker Hub became reachable through Docker normally.

The following command succeeded:

    docker pull hello-world

Docker Compose was then able to pull:

    grafana/tempo:3.0.2

without changing the Tempo service definition.

## Verification

A known public image was pulled successfully:

    docker pull hello-world

The Tempo image was then downloaded successfully.

After the image became available, Docker Compose was able to start the Tempo container and troubleshooting moved to the separate filesystem-permission issue.

This confirmed that the original HTTP 403 failure was associated with external registry access rather than the Tempo application configuration.

## Important Note

The VPN was an operational workaround that changed the network path.

It does not prove which upstream network component originally caused the HTTP 403 responses.

Possible network-path explanations should not be presented as confirmed root causes without additional evidence.

When a registry pull fails, testing a simple public image can help distinguish an image-specific problem from a broader registry-connectivity problem.

## Lesson Learned

A container image pull failure is not always a Docker or Compose configuration problem.

Testing the registry directly and attempting to pull a known public image helps isolate whether the failure belongs to:

    the image
    Docker configuration
    authentication
    or the external network path

Avoid changing application configuration until the registry path itself has been verified.
