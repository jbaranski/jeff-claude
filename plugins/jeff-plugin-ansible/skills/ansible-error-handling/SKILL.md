---
name: ansible-error-handling
description: >
  Implements robust error handling in Ansible using block/rescue/always patterns,
  retry logic with until/retries, and clear assertion patterns for graceful failure
  management.
when_to_use: >
  Use when implementing error handling in Ansible, using block/rescue/always patterns,
  creating retry logic with until/retries, handling expected failures gracefully, or
  providing clear error messages with assert and fail.
---

# Ansible Error Handling

Patterns for robust error handling in Ansible playbooks and roles.

## Block/Rescue/Always Pattern

Handle errors and perform cleanup:

```yaml
- name: Deploy application
  block:
    - name: Stop application
      ansible.builtin.systemd:
        name: myapp
        state: stopped

    - name: Deploy new version
      ansible.builtin.copy:
        src: myapp-v2.0
        dest: /usr/bin/myapp

    - name: Start application
      ansible.builtin.systemd:
        name: myapp
        state: started

  rescue:
    - name: Rollback to previous version
      ansible.builtin.copy:
        src: myapp-backup
        dest: /usr/bin/myapp

    - name: Start application (rollback)
      ansible.builtin.systemd:
        name: myapp
        state: started

    - name: Report failure
      ansible.builtin.fail:
        msg: "Deployment failed, rolled back to previous version"

  always:
    - name: Cleanup temp files
      ansible.builtin.file:
        path: /tmp/deploy-*
        state: absent
```

### Execution Flow

- **block**: Main tasks execute sequentially
- **rescue**: Runs if ANY task in block fails
- **always**: Runs regardless of success/failure

## Retry with Until

Handle transient failures with retries:

```yaml
- name: Wait for service to be ready
  ansible.builtin.uri:
    url: http://localhost:8080/health
    status_code: 200
  register: health_check
  until: health_check.status == 200
  retries: 30
  delay: 10
  # Total wait: up to 5 minutes (30 * 10s)
```

### With Command Module

```yaml
- name: Wait for PostgreSQL to accept connections
  ansible.builtin.command: pg_isready -h localhost
  register: pg_status
  until: "'accepting connections' in pg_status.stdout"
  retries: 12
  delay: 5
  changed_when: false
```

### Retry Parameters

| Parameter | Description |
|-----------|-------------|
| `until` | Condition that must be true to stop retrying |
| `retries` | Maximum number of attempts |
| `delay` | Seconds between attempts |

## Assert for Validation

Validate inputs with clear error messages:

```yaml
- name: Validate required variables
  ansible.builtin.assert:
    that:
      - app_name is defined
      - app_name | length > 0
      - app_port >= 1024
      - app_port <= 65535
    fail_msg: |
      Invalid application configuration:
      - app_name: {{ app_name | default('NOT SET') }}
      - app_port: {{ app_port | default('NOT SET') }} (must be 1024-65535)
    success_msg: "Application configuration validated"
    quiet: true
```

### Common Assertions

```yaml
# Variable defined and non-empty
- app_name is defined and app_name | trim | length > 0

# Numeric range
- app_port >= 1024 and app_port <= 65535

# Regex match
- app_name is match('^[a-z0-9-]+$')

# List has items
- app_hosts | length > 0

# Value in allowed list
- deploy_env in ['staging', 'production']
```

## Fail with Context

Provide actionable error messages:

```yaml
- name: Check prerequisites
  ansible.builtin.command: which docker
  register: docker_check
  changed_when: false
  failed_when: false

- name: Fail if Docker not installed
  ansible.builtin.fail:
    msg: |
      Docker is not installed on {{ inventory_hostname }}.

      To install Docker:
        sudo apt update
        sudo apt install docker.io

      Or use the docker role:
        ansible-playbook playbooks/install-docker.yml
  when: docker_check.rc != 0
```

## Graceful Failure Handling

Allow expected "failures":

```yaml
- name: Try to stop service
  ansible.builtin.systemd:
    name: myservice
    state: stopped
  register: stop_result
  failed_when:
    - stop_result.failed
    - "'not found' not in stop_result.msg"
  # Only fail if error is NOT "service not found"
```

### Multiple Acceptable Conditions

```yaml
- name: Add user to docker group
  ansible.builtin.command: usermod -aG docker {{ username }}
  register: group_add
  failed_when:
    - group_add.rc != 0
    - "'already a member' not in group_add.stderr"
  changed_when: group_add.rc == 0
```

## Check Before Fail

Separate checking from failing for better control:

```yaml
- name: Check if resource exists
  ansible.builtin.command: check-resource {{ resource_id }}
  register: resource_check
  changed_when: false
  failed_when: false  # Don't fail here

- name: Fail with context if missing
  ansible.builtin.fail:
    msg: |
      Resource {{ resource_id }} not found.
      Command output: {{ resource_check.stderr }}
      Hint: Ensure resource was created first.
  when: resource_check.rc != 0
```

## Error Recovery Pattern

Attempt operation, handle specific errors:

```yaml
- name: Attempt primary approach
  block:
    - name: Connect via primary endpoint
      ansible.builtin.uri:
        url: "https://{{ primary_host }}/api/health"
        validate_certs: true
      register: primary_result

  rescue:
    - name: Log primary failure
      ansible.builtin.debug:
        msg: "Primary endpoint failed: {{ primary_result.msg | default('unknown error') }}"

    - name: Try fallback endpoint
      ansible.builtin.uri:
        url: "https://{{ fallback_host }}/api/health"
        validate_certs: false
      register: fallback_result
```

## Delegate Error Handling

Run checks from controller for better error context:

```yaml
- name: Verify service endpoint from controller
  ansible.builtin.uri:
    url: "http://{{ inventory_hostname }}:{{ app_port }}/health"
    validate_certs: false
  delegate_to: localhost
  register: api_check
  failed_when: false

- name: Report service status
  ansible.builtin.fail:
    msg: |
      Cannot reach service on {{ inventory_hostname }}:{{ app_port }}
      Status: {{ api_check.status | default('connection failed') }}
      Check: Network connectivity, firewall rules, service status
  when: api_check.status | default(0) != 200
```

## Ignore Errors (Use Sparingly)

```yaml
- name: Remove optional backup
  ansible.builtin.file:
    path: /backup/old-backup.tar.gz
    state: absent
  ignore_errors: true
  register: cleanup_result

- name: Report cleanup status
  ansible.builtin.debug:
    msg: "Cleanup {{ 'successful' if not cleanup_result.failed else 'skipped' }}"
```

### When ignore_errors is Acceptable

- Non-critical cleanup tasks
- Optional operations that shouldn't block playbook
- When the result is immediately checked anyway

### Prefer failed_when

```yaml
# BETTER than ignore_errors
- name: Remove backup
  ansible.builtin.file:
    path: /backup/old-backup.tar.gz
    state: absent
  register: cleanup_result
  failed_when:
    - cleanup_result.failed
    - "'does not exist' not in cleanup_result.msg | default('')"
```

## Complete Example

```yaml
---
- name: Deploy with comprehensive error handling
  hosts: app_servers
  become: true

  tasks:
    - name: Validate configuration
      ansible.builtin.assert:
        that:
          - app_version is defined
          - app_version is match('^\d+\.\d+\.\d+$')
        fail_msg: "Invalid app_version: {{ app_version | default('NOT SET') }}"

    - name: Deploy application
      block:
        - name: Download release
          ansible.builtin.get_url:
            url: "https://releases.example.com/{{ app_version }}.tar.gz"
            dest: /tmp/app.tar.gz
          register: download
          until: download is succeeded
          retries: 3
          delay: 5

        - name: Stop current version
          ansible.builtin.systemd:
            name: myapp
            state: stopped

        - name: Extract release
          ansible.builtin.unarchive:
            src: /tmp/app.tar.gz
            dest: /opt/myapp
            remote_src: true

        - name: Start new version
          ansible.builtin.systemd:
            name: myapp
            state: started

        - name: Verify health
          ansible.builtin.uri:
            url: http://localhost:8080/health
          register: health
          until: health.status == 200
          retries: 6
          delay: 10

      rescue:
        - name: Restore previous version
          ansible.builtin.copy:
            src: /opt/myapp-backup/
            dest: /opt/myapp/
            remote_src: true

        - name: Start previous version
          ansible.builtin.systemd:
            name: myapp
            state: started

        - name: Report deployment failure
          ansible.builtin.fail:
            msg: |
              Deployment of {{ app_version }} failed.
              Previous version restored.
              Check logs: journalctl -u myapp

      always:
        - name: Cleanup download
          ansible.builtin.file:
            path: /tmp/app.tar.gz
            state: absent
```

## Related Skills

- **ansible-idempotency** - changed_when/failed_when patterns
- **ansible-fundamentals** - Core Ansible concepts
