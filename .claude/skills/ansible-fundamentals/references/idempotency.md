# Ansible Idempotency Patterns

A task is idempotent when a second run reports no changes. Native modules are idempotent already;
everything here is about `command` and `shell`, which report `changed` on every run unless told
otherwise. Every `command`/`shell` task needs `register` plus an explicit `changed_when`.

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

## Utility Script

`scripts/check_idempotency.py` in this skill's directory checks playbooks and role task files
(it runs through `uv`, which supplies PyYAML). Run it with the path to wherever this skill is installed:

```bash
uv run --script <skill-dir>/scripts/check_idempotency.py playbooks/*.yml roles/*/tasks/*.yml roles/*/handlers/*.yml
uv run --script <skill-dir>/scripts/check_idempotency.py --strict playbooks/site.yml   # info issues become warnings
uv run --script <skill-dir>/scripts/check_idempotency.py --summary playbooks/*.yml     # counts only
```

The definitive test is still running the playbook twice and confirming the second run reports `changed=0`.

The script detects:

- Command/shell tasks without `changed_when`
- Shell tasks without `set -euo pipefail`
- Tasks missing `no_log` that may contain secrets
- Tasks missing name attribute
- Short module names instead of FQCN
