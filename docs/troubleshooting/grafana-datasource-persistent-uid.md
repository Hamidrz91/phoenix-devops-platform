# Grafana Datasource Kept an Old UID

## Problem

During Grafana provisioning, the Prometheus datasource was configured with a fixed UID:

    prometheus

However, after restarting Grafana, the datasource continued using its previous randomly generated UID.

The provisioning file was correct, but Grafana did not reflect the new UID.

## Investigation

The datasource provisioning configuration contained:

    name: Prometheus
    uid: prometheus
    type: prometheus
    url: http://prometheus:9090

Grafana was also using a persistent Docker volume:

    grafana_data

Because Grafana stores its internal state in this volume, the datasource that had already been created remained stored in Grafana's database.

Restarting the container did not remove that persisted state.

## Root Cause

The existing Prometheus datasource had already been stored in Grafana's persistent database with its previous UID.

Changing the provisioning file did not automatically replace the persisted datasource identity.

The old datasource state survived container restarts because it was stored in the Grafana Docker volume.

## Solution

Only the Grafana container and Grafana data volume were removed.

The PostgreSQL and Prometheus volumes were left untouched.

Grafana was then recreated from the Docker Compose configuration.

During startup, Grafana provisioned the Prometheus datasource again using the fixed UID:

    prometheus

The datasource provisioning configuration remained mounted read-only inside the container.

## Verification

The Grafana datasource API was queried:

    GET /api/datasources/uid/prometheus

The response confirmed:

    name: Prometheus
    uid: prometheus
    url: http://prometheus:9090
    isDefault: true

The datasource health endpoint was also tested.

Grafana returned:

    status: OK
    Successfully queried the Prometheus API.

The Phoenix dashboard was then found successfully through the Grafana API with the UID:

    phoenix-overview

## Important Note

Deleting a Docker volume removes persistent application state.

This should only be done when the impact is understood.

In this case, only the Grafana development volume was reset. PostgreSQL and Prometheus persistent data were not deleted.

In a production Grafana environment containing important dashboards, users, alerts, or configuration, deleting the Grafana volume would require much more careful planning.

## Lesson Learned

Restarting or recreating a container is different from resetting its persistent data.

Docker volumes can preserve old application state even when configuration files have changed.

When troubleshooting provisioned applications, always consider both:

    Configuration on disk
    Persistent application state

A correct configuration file does not necessarily mean the application has replaced previously persisted state.
