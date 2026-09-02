# Ansible Vault Decryption Failure

## Problem

During the Phoenix monitoring deployment, Ansible failed to use encrypted variables from `ansible/group_vars/phoenix/vault.yml`.

The deployment produced a Vault decryption error similar to:

    Decryption failed (no vault secrets were found that could decrypt)

A simple test checking whether the variable was defined had previously succeeded, which initially made the Vault configuration appear valid.

## Investigation

The encrypted Vault file itself was still present and had not been accidentally modified.

However, checking only whether a variable was defined did not necessarily force Ansible to decrypt and evaluate its actual value.

When the encrypted value was actually used, decryption failed.

The problem was traced to inconsistent manual Vault password entry.

## Root Cause

The password being manually entered when running Ansible did not match the password that had originally been used to encrypt the Vault values.

Because Vault passwords were entered manually, typing mistakes and password inconsistency could easily cause decryption failures.

## Solution

A local Vault password file was created:

    .vault_pass

The file was protected with restrictive permissions:

    chmod 600 .vault_pass

It was also added to `.gitignore`:

    .vault_pass

The required secrets were then encrypted using the same Vault identity and password file.

Ansible commands were changed to use:

    --vault-id phoenix@.vault_pass

Example:

    ansible-playbook \
      -i ansible/inventory.ini \
      ansible/playbook.yml \
      --ask-become-pass \
      --vault-id phoenix@.vault_pass

## Verification

An encrypted variable was tested by forcing Ansible to evaluate its value rather than only checking whether the variable existed.

The deployment then completed successfully.

A final Ansible run produced:

    ok=7
    changed=0
    unreachable=0
    failed=0

This also confirmed deployment idempotency.

## Security Notes

The Vault password file must never be committed to Git.

The project therefore ignores:

    .vault_pass
    .env

Both files contain local secrets only.

For a production environment, the Vault password should ideally be supplied through a CI/CD secret store or another dedicated secrets-management system rather than stored beside the repository on the deployment server.

## Lesson Learned

A variable being "defined" does not prove that an Ansible Vault secret can actually be decrypted.

Vault verification should force evaluation of the encrypted value.

Using a consistent Vault identity and protected password source also reduces errors caused by manually entering Vault passwords.
