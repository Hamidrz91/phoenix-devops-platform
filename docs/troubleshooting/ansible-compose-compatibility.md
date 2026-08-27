# Ansible Docker Compose Compatibility Troubleshooting

## Problem

While testing the Phoenix deployment with Ansible in check mode, the Docker Compose module returned multiple warnings.

The environment was using:

    community.docker 3.7.0
    Docker Compose 5.4.0

The warnings included:

    Event line is missing dry-run mode marker

The module was able to communicate with Docker Compose, but it could not correctly interpret the dry-run output.

## Investigation

The installed community.docker collection version was checked with:

    ansible-galaxy collection list community.docker

The system had:

    community.docker 3.7.0

Docker Compose version was:

    Docker Compose version v5.4.0

The Ansible Docker Compose check was then executed with:

    ansible -i ansible/inventory.ini phoenix \
      -m community.docker.docker_compose_v2 \
      -a "project_src=$PWD state=present" \
      --check

The command completed, but produced several parsing warnings.

A Docker container check confirmed that check mode had not actually created the phoenix-app container.

## Root Cause

The installed community.docker collection was older than the Docker Compose version used in the Phoenix environment.

The older collection could not correctly parse the newer Docker Compose dry-run output format.

## Solution

The community.docker collection was upgraded and pinned to:

    community.docker 4.8.8

The required version was documented in:

    ansible/requirements.yml

After installing version 4.8.8, Ansible used the newer collection from the user collection path.

## Verification

The same Docker Compose Ansible check was executed again.

This time:

    localhost | CHANGED

was returned without the previous dry-run parsing warnings.

A container check also confirmed that check mode did not create the phoenix-app container.

## Lesson Learned

Automation tools and their plugins must be compatible with the versions of the external tools they control.

A module may still appear to work while producing parsing warnings that indicate version incompatibility.

For reproducible infrastructure automation, important Ansible collection versions should be explicitly pinned and documented in the project.
