# Tempo Failed To Write To Docker Volume

## Problem

After the Grafana Tempo image was successfully pulled, the Tempo container entered a restart loop.

The container logs showed:

    failed to init module services
    failed to create store
    mkdir /data/tempo/blocks: permission denied

Tempo could start reading its configuration, but it could not create the directories required for local trace storage.

## Investigation

The configured Tempo storage paths were located under:

    /data/tempo

A Docker named volume was mounted at this location.

The user configured inside the Tempo image was inspected:

    docker image inspect grafana/tempo:3.0.2 --format 'Tempo image user: {{.Config.User}}'

The result was:

    Tempo image user: 10001:10001

The Docker volume directory on the host was then inspected.

Its ownership and permissions were:

    owner=0:0 mode=755

This meant the volume directory belonged to root, while Tempo was running as UID and GID:

    10001:10001

With mode 755, the Tempo process could read and enter the directory but could not create new directories inside it.

## Root Cause

The Tempo container was running as:

    10001:10001

while the Docker volume mountpoint was owned by:

    root:root

with permissions:

    0755

Because the Tempo process was not the owner of the directory, it did not have write permission required to create:

    /data/tempo/blocks
    /data/tempo/wal

The failure was therefore a filesystem ownership mismatch between the container process and the persistent Docker volume.

## Solution

A manual ownership change was first used to prove the diagnosis:

    sudo chown -R 10001:10001 <tempo-volume-mountpoint>

After the ownership change, Tempo started successfully.

However, a manual host-level chown was not kept as the final solution.

The Tempo volume was changed to an explicitly named external Docker volume:

    tempo_data:
      external: true
      name: phoenix_tempo_data

Ansible was then made responsible for creating the volume:

    - name: Ensure Tempo data volume exists
      community.docker.docker_volume:
        name: phoenix_tempo_data
        state: present
      register: tempo_volume

Ansible also manages the filesystem ownership:

    - name: Set Tempo data volume ownership
      ansible.builtin.file:
        path: "{{ tempo_volume.volume.Mountpoint }}"
        state: directory
        owner: "10001"
        group: "10001"
        mode: "0755"
        recurse: true
      become: true

This made the permission requirement part of the reproducible infrastructure configuration.

## Verification

After Ansible created and prepared the volume, its ownership was verified as:

    owner=10001:10001 mode=755

Tempo started successfully.

Its readiness endpoint returned:

    ready

The complete tracing pipeline was then tested successfully:

    Phoenix -> OpenTelemetry -> Alloy -> Tempo -> Grafana

Real Phoenix traces were stored in Tempo and queried from Grafana.

A later Ansible run completed with:

    changed=0
    failed=0

This confirmed that the final volume-management solution was also idempotent.

## Important Note

The manual chown command was useful as a diagnostic step, but it was not the final infrastructure solution.

Manual filesystem fixes are easy to lose when:

    a server is rebuilt
    a volume is recreated
    another environment is deployed

Encoding the required ownership in Ansible makes the behavior reproducible.

The UID and GID should also be treated as image-specific implementation details and verified if the Tempo image is changed in the future.

## Lesson Learned

Persistent container storage must be writable by the user running inside the container.

A healthy Docker volume does not automatically mean that the application process has permission to write to it.

When a container reports:

    permission denied

on a mounted path, inspect both:

    the container runtime UID/GID
    the host-side volume ownership and permissions

Once the cause is confirmed, prefer infrastructure automation over a one-time manual permission fix.
