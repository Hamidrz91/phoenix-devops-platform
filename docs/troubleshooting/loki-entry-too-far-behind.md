# Loki Rejected Old Docker Logs

## Problem

After Grafana Alloy was connected to Docker and configured to forward container logs to Loki, Alloy started successfully and all components reported healthy.

However, the Alloy logs showed an HTTP 400 error from Loki:

    entry too far behind

The rejected log entry had a timestamp that was significantly older than the newest entries already accepted by Loki.

## Investigation

Alloy was configured to discover Docker containers and read their logs using:

    discovery.docker
    loki.source.docker

When Alloy started for the first time, it discovered existing containers that already contained older Docker log history.

Alloy attempted to send some of this historical backlog to Loki.

Loki accepted recent entries, but rejected entries that were too old for the allowed out-of-order ingestion window.

The logging pipeline itself was working because recent Phoenix application logs were successfully stored and queried from Loki.

## Root Cause

The issue was not a connectivity failure between Alloy and Loki.

The problem was old Docker log entries being forwarded during the initial collection.

Those entries were older than the timestamp range Loki was willing to accept for the existing log stream.

## Solution

A processing stage was added between the Docker log source and Loki.

The Alloy pipeline was changed from:

    loki.source.docker
        ->
    loki.write

to:

    loki.source.docker
        ->
    loki.process
        ->
    loki.write

The processing stage drops log entries older than 24 hours:

    loki.process "drop_old_logs" {
      stage.drop {
        older_than          = "24h"
        drop_counter_reason = "too_old"
      }

      forward_to = [loki.write.local.receiver]
    }

The Docker log source was then changed to forward entries to this processing stage.

## Verification

Alloy was recreated with the updated configuration.

The health endpoints returned:

    Alloy is ready.
    All Alloy components are healthy.

Recent Alloy logs no longer contained:

    entry too far behind
    status=400
    dropping data

New Phoenix application requests were then generated.

The logs were successfully queried from Loki and included recent entries such as:

    GET /health HTTP/1.1" 200

This confirmed that recent logs continued flowing through the complete pipeline:

    Docker -> Alloy -> Loki -> Grafana

## Important Note

The 24-hour value is a filtering decision for this Phoenix lab environment.

It is not Loki retention.

Retention controls how long Loki keeps data after ingestion, while this Alloy processing rule controls which old log entries are allowed to reach Loki in the first place.

A production environment may require a different value depending on operational and compliance requirements.

## Lesson Learned

A healthy log collector does not guarantee that every historical log entry will be accepted by the backend.

When introducing centralized logging to existing containers, old log history may be processed during the first discovery.

Timestamp-related ingestion errors should be investigated separately from network or service-health failures.

Filtering stale backlog before ingestion can keep the logging pipeline clean while allowing current logs to continue flowing normally.
