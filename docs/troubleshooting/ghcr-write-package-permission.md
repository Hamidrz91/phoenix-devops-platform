# GHCR Write Package Permission Troubleshooting

## Problem

The Phoenix GitHub Actions workflow successfully built the Docker image and logged in to GitHub Container Registry (GHCR), but failed while pushing the image.

Error:

    denied: permission_denied: write_package

## Investigation

The CI workflow already had the required permissions:

    permissions:
      contents: read
      packages: write

Authentication to GHCR using GITHUB_TOKEN was also successful.

The failure happened only during the Docker push step.

## Root Cause

The phoenix-app package had originally been pushed manually to GHCR.

Because the package already existed, the GitHub repository did not automatically have write access to that package through GitHub Actions.

GITHUB_TOKEN could authenticate successfully, but it could not write to the existing package.

## Solution

In the GHCR package settings:

1. Opened the phoenix-app package.
2. Opened Package settings.
3. Located Manage Actions access.
4. Added the repository:

    Hamidrz91/phoenix-devops-platform

5. Granted the repository Write access.
6. Re-ran the failed GitHub Actions job.

## Verification

The second workflow attempt completed successfully:

    Build Docker image        -> success
    Log in to GHCR            -> success
    Push Docker image to GHCR -> success

The image was then pulled from GHCR and verified successfully.

## Lesson Learned

Successful authentication to a container registry does not automatically mean the workflow has permission to modify an existing package.

Workflow permissions and package-level permissions are separate concerns.

When a GHCR package is created manually before CI/CD automation is introduced, repository access to that package should be verified before using GITHUB_TOKEN for automated publishing.
