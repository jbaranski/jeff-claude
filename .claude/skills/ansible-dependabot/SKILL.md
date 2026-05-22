---
name: ansible-dependabot
description: >
  Configure Dependabot to keep Ansible Python tooling (ansible, ansible-lint) up to date
  via the uv ecosystem. Covers what Dependabot can and cannot automate for Ansible projects.
when_to_use: >
  Use when setting up Dependabot for an Ansible project, adding automated dependency
  updates for Ansible tooling, or asked to "set up Dependabot for Ansible".
---

# Dependabot for Ansible

Dependabot covers the **Python tooling side** of Ansible (the `ansible`, `ansible-lint`,
and related packages managed by `uv`). It does **not** support Ansible Galaxy collections
(`requirements.yml`) — see the note at the bottom.

## What Dependabot Covers

| Dependency type | Supported | Ecosystem |
|---|---|---|
| `ansible`, `ansible-lint`, etc. (`pyproject.toml`) | ✅ Yes | `uv` |
| GitHub Actions workflows | ✅ Yes | `github-actions` |
| Ansible Galaxy collections (`requirements.yml`) | ❌ No | — |

## Steps

1. Locate the `pyproject.toml` that manages Ansible tooling. It is typically at the
   repo root or in an `ansible/` subdirectory. Check:

   ```bash
   find . -name "pyproject.toml" | grep -v ".venv"
   ```

2. Check if `.github/dependabot.yml` already exists.

3. Add a `uv` entry for each directory containing a `pyproject.toml`. For example,
   if `pyproject.toml` is in the repo root:

   ```yaml
   version: 2
   updates:
     - package-ecosystem: 'github-actions'
       directory: '/'
       schedule:
         interval: 'weekly'

     - package-ecosystem: 'uv'
       directory: '/'
       schedule:
         interval: 'weekly'
   ```

   If `pyproject.toml` lives in an `ansible/` subdirectory instead:

   ```yaml
   version: 2
   updates:
     - package-ecosystem: 'github-actions'
       directory: '/'
       schedule:
         interval: 'weekly'

     - package-ecosystem: 'uv'
       directory: '/ansible'
       schedule:
         interval: 'weekly'
   ```

4. Commit and push `.github/dependabot.yml`. Dependabot will open PRs when new
   versions of `ansible`, `ansible-lint`, or other `uv`-managed packages are released.

## What Dependabot Cannot Do

Ansible Galaxy collection versions pinned in `requirements.yml` are not a supported
Dependabot ecosystem. Those updates must be handled manually or via Renovate Bot.

See `TODO.md` in the repo root for the open discussion on automating collection updates.

## Additional Resources

- https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot
- https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference

## Related Skills

- **ansible-fundamentals** - uv run conventions and collection management
- **jeff-skill-install-dependabot** - General Dependabot setup across all ecosystems
