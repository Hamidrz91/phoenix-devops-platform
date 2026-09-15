# Docker Compose Config Exposed Resolved Secret Values

## Problem

While validating the Phoenix Docker Compose configuration, the following command was used:

    docker compose config

The command successfully rendered the fully resolved Compose configuration.

However, environment variables from the local `.env` file were expanded before being printed.

As a result, sensitive values such as:

    DB_PASSWORD

were displayed in plaintext in the terminal output.

## Investigation

The Phoenix Compose file references environment variables such as:

    DB_PASSWORD: ${DB_PASSWORD}

The actual value is stored in:

    .env

The `.env` file itself is protected from Git by `.gitignore`.

However, running:

    docker compose config

does not preserve the variable reference.

Instead, Docker Compose resolves the environment variable and prints the resulting value.

Therefore:

    ${DB_PASSWORD}

became the real database password in the rendered output.

This was not a Git leak.

It was a terminal-output exposure caused by rendering the resolved Compose configuration.

## Root Cause

The command:

    docker compose config

outputs the effective Compose configuration after environment-variable interpolation.

Sensitive variables referenced by Compose may therefore appear in plaintext.

The secret remained protected in source control, but it was exposed in command output.

## Solution

The exposed PostgreSQL credential was rotated.

A new random password was generated without printing the password itself:

    NEW_DB_PASSWORD="$(openssl rand -hex 24)"

The new password was encrypted with Ansible Vault using variable-level encryption.

The encrypted block for:

    vault_db_password

was replaced while leaving the Grafana credential unchanged.

The PostgreSQL role password was then updated directly:

    ALTER ROLE phoenix WITH PASSWORD '...';

The Ansible playbook was executed afterward to regenerate:

    .env

and recreate the Phoenix application with the new credential.

The temporary shell variable and temporary encrypted block were then removed.

## Verification

The PostgreSQL role accepted the new password.

The Ansible playbook regenerated the Phoenix environment file successfully.

The application database endpoint returned:

    {"database":"connected"}

The temporary password variable was removed from the shell:

    unset NEW_DB_PASSWORD

The temporary file was also deleted:

    rm -f /tmp/vault_db_password.block

The local secret files remained excluded from Git:

    .env
    .vault_pass

and the final Git status did not include either file.

## Important Note

A file being excluded from Git does not mean its contents can never be exposed.

Commands that render resolved configuration may print sensitive values.

This includes tools that expand environment variables or combine configuration layers before displaying the final result.

When sharing command output, avoid pasting complete resolved configuration if it may contain secrets.

Prefer targeted inspection commands that show only the fields needed for troubleshooting.

## Lesson Learned

Secrets can be exposed through observability and troubleshooting workflows even when secret storage itself is configured correctly.

Protecting secrets requires attention to:

    source control
    terminal output
    logs
    debugging commands
    generated configuration

When a credential is exposed, rotation is safer than assuming the exposure has no consequence.

The final Phoenix workflow now treats resolved configuration output as potentially sensitive.
