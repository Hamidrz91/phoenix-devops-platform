# Ansible Galaxy HTTP 403 Troubleshooting

## Problem

While installing the required Ansible collection for the Phoenix deployment, the installation failed when connecting to Ansible Galaxy.

The command was:

    ansible-galaxy collection install -r ansible/requirements.yml

The error was:

    ERROR! Error when finding available api versions from default
    (https://galaxy.ansible.com)
    HTTP Code: 403
    Message: Forbidden

## Investigation

To determine whether the issue was specific to ansible-galaxy or related to network access to Ansible Galaxy, the API endpoint was tested directly:

    curl -sS -o /dev/null -w "HTTP %{http_code}\n" https://galaxy.ansible.com/api/

The result was:

    HTTP 403

This confirmed that the Phoenix server could reach the service, but access to the Galaxy API was being rejected.

## Root Cause

The failure was related to access to the Ansible Galaxy API from the Phoenix environment.

The problem was not caused by the collection version or by the Ansible requirements file.

## Solution

Instead of downloading the collection from Ansible Galaxy, the project was configured to install the collection directly from its official Git repository.

The requirements file was changed to:

    ---
    collections:
      - name: https://github.com/ansible-collections/community.docker.git
        type: git
        version: "4.8.8"

The collection was then installed using:

    ansible-galaxy collection install -r ansible/requirements.yml

## Verification

The installation completed successfully.

The installed collection was verified with:

    ansible-galaxy collection list community.docker

The result showed:

    community.docker 4.8.8

from the user collection path.

The Docker Compose Ansible check was then repeated successfully without the previous compatibility warnings.

## Lesson Learned

Dependency installation should not rely on a single external distribution service when another official source is available.

Using a pinned Git source made the Ansible dependency explicit and reproducible while avoiding the Galaxy API access issue.

When troubleshooting package or collection installation problems, verifying the upstream service independently can help separate dependency problems from network or access problems.
