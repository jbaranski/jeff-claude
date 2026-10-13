---
name: ansible-fundamentals
description: >
  Ansible conventions for Debian and Docker infrastructure: FQCN modules, uv run, idempotent
  command/shell tasks, pipefail, no_log, capitalized task and handler names, and ansible_facts —
  plus on-demand references for idempotency, error handling, playbook and role design, systemd
  timer jobs, and Dependabot.
when_to_use: >
  Use whenever writing, editing, reviewing, or running Ansible playbooks, roles, tasks, handlers,
  or templates.
---

# Ansible

Targets are Debian hosts, with Docker managed through `community.docker`. Python tooling (ansible,
ansible-lint) is managed with `uv`.

## Rules

1. **Run everything through uv**: `uv run ansible-playbook ...`, `uv run ansible-lint`, `uv run ansible-galaxy ...`.
2. **FQCN for every module**: `ansible.builtin.apt`, `community.docker.docker_container` — never short names.
3. **Prefer native modules** over `command`/`shell`. Use `command` when no module exists; `shell` only for pipes, redirects or globs.
4. **Every `command`/`shell` task has `register` and an explicit `changed_when`** (`false` for read-only checks). Add `failed_when` to allow only the specific failures you expect — never a blanket `failed_when: false` or `ignore_errors` on real work.
5. **`shell` with pipes or redirects** starts with `set -euo pipefail` and sets `executable: /bin/bash`.
6. **Idempotent**: a second run reports `changed=0`.
7. **Names start with an uppercase action verb** — tasks, plays and handlers alike (`Install nginx`, `Restart docker`); ansible-lint enforces this. `notify` must match the handler name exactly.
8. **Read facts through `ansible_facts`** (`ansible_facts['os_family']`), not the injected `ansible_*` variables.
9. **Secrets** live in gitignored `group_vars`/`host_vars` files or GitHub Actions secrets — no third-party secrets manager. In CI, pass them through `env:` and read them with `lookup('ansible.builtin.env', 'NAME')`, never as `-e` arguments. Every task that touches a secret has `no_log: true`.
10. **Services** through `ansible.builtin.systemd_service`; recurring jobs as systemd timers, not cron.

## Working efficiently

- For a small change, read only the files you are changing and their direct neighbours (the role's `defaults/main.yml`, `handlers/main.yml`, the templates involved). Don't survey the whole repo.
- Open a reference below only when the task needs it.
- Verify with `uv run ansible-lint <changed files>` and `uv run ansible-playbook --syntax-check <playbook>`. Use `--check --diff` against a host only when asked.

## References (read on demand)

| Read                                                                     | When                                                                               |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| [references/idempotency.md](references/idempotency.md)                   | Writing `command`/`shell` tasks, `changed_when`/`failed_when`, check-before-create |
| [references/error-handling.md](references/error-handling.md)             | `block`/`rescue`/`always`, retries with `until`, `assert`, rollback                |
| [references/playbook-design.md](references/playbook-design.md)           | New playbooks, present/absent state, play section order, handler flush timing      |
| [references/role-design.md](references/role-design.md)                   | New roles, defaults vs vars, variable naming, handlers, `meta/main.yml`            |
| [references/systemd-timer-jobs.md](references/systemd-timer-jobs.md)     | Any recurring job: script + oneshot service + timer, syslog logging                |
| [references/modules-and-commands.md](references/modules-and-commands.md) | Choosing a module, collections in use, common `ansible-playbook` invocations       |
| [references/dependabot.md](references/dependabot.md)                     | Setting up Dependabot for an Ansible repo                                          |

`scripts/check_idempotency.py` flags common idempotency problems in playbooks and role task files:
`uv run --script <skill-dir>/scripts/check_idempotency.py playbooks/*.yml roles/*/tasks/*.yml`.
