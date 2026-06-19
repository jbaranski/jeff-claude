---
name: ansible-idempotency
description: >
  Techniques for writing truly idempotent Ansible tasks using changed_when,
  failed_when, and check-before-create patterns to eliminate spurious "changed"
  reports.
when_to_use: >
  Use when writing idempotent Ansible tasks, using command or shell modules,
  implementing changed_when and failed_when directives, creating check-before-create
  patterns, or troubleshooting tasks that always show "changed".
---

# Ansible Idempotency Patterns

Techniques for ensuring Ansible tasks are truly idempotent - producing the same result
whether run once or multiple times.

## Core Directives

### changed_when

Controls when Ansible reports a task as "changed". Critical for `command` and `shell` modules
which always report changed by default.

```yaml
- name: Check if service exists
  ansible.builtin.command: systemctl status myservice
  register: service_check
  changed_when: false # Read-only operation, never changes anything
```

### failed_when

Controls when Ansible considers a task failed. Allows graceful handling of expected errors.

```yaml
- name: Check resource existence
  ansible.builtin.command: check-resource {{ resource_id }}
  register: check_result
  failed_when: false # Don't fail, we'll check the result ourselves
```

### register

Captures task output for use in `changed_when` and `failed_when` expressions.

```yaml
- name: Run command
  ansible.builtin.command: some-command
  register: cmd_result
  # Now cmd_result.rc, cmd_result.stdout, cmd_result.stderr are available
```

## Pattern 1: Detect Actual Changes

Make commands report "changed" only when something actually changed:

```yaml
- name: Enable Apache module
  ansible.builtin.command: a2enmod {{ module_name }}
  register: mod_result
  changed_when: "'already enabled' not in mod_result.stdout"
  failed_when:
    - mod_result.rc != 0
    - "'already enabled' not in mod_result.stdout"
```

**Key pattern**: Detect specific output that indicates no change occurred.

## Pattern 2: Check Before Create

Check if a resource exists before creating it:

```yaml
- name: Check if database exists
  ansible.builtin.shell: |
    set -o pipefail
    psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "{{ db_name }}"
  args:
    executable: /bin/bash
  register: db_exists
  changed_when: false # Checking doesn't change anything
  failed_when: false # Not finding it isn't a failure

- name: Create database
  ansible.builtin.command: createdb -U postgres {{ db_name }}
  when: db_exists.rc != 0 # Only create if doesn't exist
  register: create_result
  changed_when: create_result.rc == 0
```

## Pattern 3: Verify After Create

Confirm resource creation succeeded:

```yaml
- name: Run database migration
  ansible.builtin.command: /opt/app/bin/migrate up
  register: migrate_result
  changed_when: true

- name: Verify migration succeeded
  ansible.builtin.command: /opt/app/bin/migrate status
  register: verify_result
  changed_when: false
  failed_when: "'pending' in verify_result.stdout"
```

## Pattern 4: Conditional Change Detection

Use output content to determine if change occurred:

```yaml
- name: Update cluster configuration
  ansible.builtin.command: update-config --apply
  register: update_result
  changed_when: "'Configuration updated' in update_result.stdout"
  failed_when: "'Error' in update_result.stderr"
```

### Common Patterns

| Output Indicator      | changed_when Expression                   |
| --------------------- | ----------------------------------------- |
| "already exists"      | `"'already exists' not in result.stderr"` |
| "no changes"          | `"'no changes' not in result.stdout"`     |
| "created"             | `"'created' in result.stdout"`            |
| "updated"             | `"'updated' in result.stdout"`            |
| Exit code 0 = created | `result.rc == 0`                          |

## Pattern 5: Multiple Failure Conditions

Allow specific "failures" that are actually expected:

```yaml
- name: Run database migration
  ansible.builtin.command: /usr/bin/migrate-database
  register: migrate_result
  failed_when:
    - migrate_result.rc != 0
    - "'already applied' not in migrate_result.stdout"
    - "'no pending migrations' not in migrate_result.stdout"
  changed_when: "'applied' in migrate_result.stdout and 'already' not in migrate_result.stdout"
```

## Pattern 6: Read-Only Operations

Mark read-only operations as never changed:

```yaml
# Checking status
- name: Get service status
  ansible.builtin.command: systemctl status nginx
  register: service_status
  changed_when: false
  failed_when: false

# Gathering information
- name: List installed packages
  ansible.builtin.command: dpkg -l
  register: package_list
  changed_when: false

# Verification checks
- name: Verify service is running
  ansible.builtin.command: systemctl is-active nginx
  register: nginx_status
  changed_when: false
  failed_when: false
```

## Pattern 7: Retry Until Success

Use `until` for operations that may need retries:

```yaml
- name: Wait for service to be ready
  ansible.builtin.uri:
    url: http://localhost:8080/health
    status_code: 200
  register: health_check
  until: health_check.status == 200
  retries: 30
  delay: 10
  # Total wait: up to 5 minutes
```

With command:

```yaml
- name: Wait for application port to be available
  ansible.builtin.command: ss -tlnp sport = :{{ app_port }}
  register: port_check
  until: port_check.rc == 0 and port_check.stdout != ""
  retries: 12
  delay: 5
  changed_when: false
```

## Pattern 8: Set Facts for State

Use facts to track state across tasks:

```yaml
- name: Check if nginx service is enabled
  ansible.builtin.command: systemctl is-enabled nginx
  register: nginx_enabled
  failed_when: false
  changed_when: false

- name: Set service state facts
  ansible.builtin.set_fact:
    nginx_is_enabled: '{{ nginx_enabled.rc == 0 }}'
    nginx_is_active: "{{ 'enabled' in nginx_enabled.stdout }}"

- name: Enable nginx service
  ansible.builtin.command: systemctl enable nginx
  when: not nginx_is_enabled
  register: enable_result
  changed_when: enable_result.rc == 0
```

## Anti-Patterns to Avoid

### Always Changed

```yaml
# BAD - Always shows changed
- name: Check status
  ansible.builtin.command: systemctl status app

# GOOD
- name: Check status
  ansible.builtin.command: systemctl status app
  register: status_check
  changed_when: false
  failed_when: false
```

### Silent Failure Suppression

```yaml
# BAD - Hides all errors
- name: Critical operation
  ansible.builtin.command: important-command
  failed_when: false

# GOOD - Only allow expected "errors"
- name: Critical operation
  ansible.builtin.command: important-command
  register: result
  failed_when:
    - result.rc != 0
    - "'expected condition' not in result.stderr"
```

### No Output Capture

```yaml
# BAD - Can't check results
- name: Run command
  ansible.builtin.command: create-resource

# GOOD
- name: Run command
  ansible.builtin.command: create-resource
  register: result
  changed_when: "'created' in result.stdout"
```

## Shell Script Requirements

Use strict error handling in shell scripts:

```yaml
- name: Run pipeline
  ansible.builtin.shell: |
    set -euo pipefail
    cat data.txt | grep pattern | sort | uniq
  args:
    executable: /bin/bash
  register: pipeline_result
  changed_when: false
```

### Why set -euo pipefail?

| Flag          | Purpose                      |
| ------------- | ---------------------------- |
| `-e`          | Exit on any command failure  |
| `-u`          | Error on undefined variables |
| `-o pipefail` | Catch errors in pipelines    |

## Testing Idempotency

Verify playbooks are idempotent by running twice:

```bash
# First run - may show changes
uv run ansible-playbook playbooks/setup.yml

# Second run - should show 0 changes
uv run ansible-playbook playbooks/setup.yml

# If second run shows changes, playbook is NOT idempotent
```

## Common changed_when Expressions

```yaml
# Never changed (read-only)
changed_when: false

# Always changed (one-time operations)
changed_when: true

# Based on output content
changed_when: "'created' in result.stdout"
changed_when: "'already exists' not in result.stderr"
changed_when: "'updated' in result.stdout"

# Based on return code
changed_when: result.rc == 0
changed_when: result.rc != 1

# Complex conditions
changed_when:
  - result.rc == 0
  - "'no changes' not in result.stdout"
```

## Utility Script

Use the idempotency checker to analyze playbooks for common issues:

```bash
# Check a single playbook
${CLAUDE_PLUGIN_ROOT}/skills/ansible-idempotency/scripts/check_idempotency.py ansible/playbooks/my-playbook.yml

# Check multiple playbooks
${CLAUDE_PLUGIN_ROOT}/skills/ansible-idempotency/scripts/check_idempotency.py ansible/playbooks/*.yml

# Strict mode (info issues become warnings)
${CLAUDE_PLUGIN_ROOT}/skills/ansible-idempotency/scripts/check_idempotency.py --strict ansible/playbooks/my-playbook.yml

# Summary only
${CLAUDE_PLUGIN_ROOT}/skills/ansible-idempotency/scripts/check_idempotency.py --summary ansible/playbooks/*.yml
```

The script detects:

- Command/shell tasks without `changed_when`
- Shell tasks without `set -euo pipefail`
- Tasks missing `no_log` that may contain secrets
- Tasks missing name attribute
- Use of deprecated short module names (non-FQCN)

Script location: `${CLAUDE_PLUGIN_ROOT}/skills/ansible-idempotency/scripts/check_idempotency.py`

## Related Skills

- **ansible-error-handling** - Block/rescue patterns
- **ansible-fundamentals** - Module selection (prefer native modules)
