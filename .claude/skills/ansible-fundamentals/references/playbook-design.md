# Ansible Playbook Design

## State-Based Playbook Pattern

Design playbooks to handle both creation and removal via a `state` variable.

### Core Pattern

```yaml
---
- name: Manage admin user account
  hosts: all
  become: true

  vars:
    admin_state: present # or absent

  tasks:
    - name: Create admin user
      ansible.builtin.user:
        name: '{{ admin_name }}'
        groups: '{{ admin_groups }}'
        state: '{{ admin_state }}'

    - name: Configure SSH key
      ansible.posix.authorized_key:
        user: '{{ admin_name }}'
        key: '{{ admin_ssh_key }}'
        state: '{{ admin_state }}'
      when: admin_state == 'present'
```

### Usage

```bash
# Create user (default)
uv run ansible-playbook playbooks/manage-admin.yml \
  -e "admin_name=alice" \
  -e "admin_ssh_key='ssh-ed25519 AAAA...'"

# Remove user
uv run ansible-playbook playbooks/manage-admin.yml \
  -e "admin_name=alice" \
  -e "admin_state=absent"
```

## Play Structure

### Recommended Play Sections

Order sections consistently across all playbooks:

```yaml
---
- name: Descriptive play name
  hosts: target_group
  become: true
  gather_facts: true

  vars:
    # Play-level variables
    app_version: '2.0.0'

  vars_files:
    # External variable files
    - vars/secrets.yml

  pre_tasks:
    # Tasks that must run before roles
    - name: Update apt cache
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600

  roles:
    # Role includes
    - role: common
    - role: app_deploy
      vars:
        deploy_version: '{{ app_version }}'

  tasks:
    # Play-specific tasks
    - name: Verify deployment
      ansible.builtin.uri:
        url: http://localhost:8080/health

  post_tasks:
    # Cleanup or finalization
    - name: Send deployment notification
      ansible.builtin.debug:
        msg: 'Deployment complete'

  handlers:
    # Event-triggered tasks
    - name: Restart app
      ansible.builtin.systemd_service:
        name: myapp
        state: restarted
```

## Variable Organization

### Organizing Variables

```text
ansible/
├── group_vars/
│   ├── all.yml           # Variables for ALL hosts
│   ├── webservers.yml    # Web server hosts
│   └── db_servers.yml    # Database server hosts
├── host_vars/
│   ├── web01.yml         # Host-specific overrides
│   └── web02.yml
└── playbooks/
    └── deploy.yml        # Uses vars: for playbook-specific
```

## Task Organization with Includes

### When to Split Tasks

Split playbook tasks into separate files when:

- Tasks exceed 50 lines
- Logical groupings emerge (networking, storage, users)
- Conditional sections can be skipped entirely

### Include Patterns

```yaml
# playbooks/setup-webserver.yml
---
- name: Setup web server
  hosts: webservers
  become: true

  tasks:
    - name: Install and configure nginx
      ansible.builtin.include_tasks: tasks/nginx.yml

    - name: Configure SSL
      ansible.builtin.include_tasks: tasks/ssl.yml
      when: setup_ssl | default(true)

    - name: Deploy application
      ansible.builtin.include_tasks: tasks/app-deploy.yml
      when: inventory_hostname == groups['webservers'][0]
```

## Handler Execution Order

Handlers run:

1. At the end of each section of a play (`pre_tasks`, then `roles` + `tasks`, then `post_tasks`)
2. In the order they are defined, not the order they were notified
3. Only once per flush, even if notified multiple times

`notify` must match the handler's `name` exactly, including case.

Force immediate handler execution:

```yaml
- name: Update critical config
  ansible.builtin.template:
    src: config.j2
    dest: /etc/app/config.yml
  notify: Restart app

- name: Flush handlers now
  ansible.builtin.meta: flush_handlers

- name: Verify app is running
  ansible.builtin.uri:
    url: http://localhost:8080/health
```

## Playbook Validation

### Pre-flight Checks

Add validation at the start of playbooks:

```yaml
---
- name: Deploy application
  hosts: app_servers
  become: true

  tasks:
    - name: Validate required variables
      ansible.builtin.assert:
        that:
          - app_version is defined
          - app_version | regex_search('^\d+\.\d+\.\d+$')
          - deploy_env in ['staging', 'production']
        fail_msg: 'Invalid configuration. Check app_version and deploy_env.'

    - name: Check disk space
      ansible.builtin.assert:
        that: ansible_facts['mounts'] | selectattr('mount', 'equalto', '/') | map(attribute='size_available') | first > 1073741824
        fail_msg: 'Insufficient disk space. Need at least 1GB free.'
```

## Template Patterns

### Playbook Template Structure

```yaml
---
# playbooks/template-playbook.yml
# Description: [What this playbook does]
# Usage: uv run ansible-playbook playbooks/template-playbook.yml -e "var=value"
# Requirements: [Any prerequisites]

- name: [Descriptive play name]
  hosts: [target_group]
  become: [true/false]
  gather_facts: [true/false]

  vars:
    # Configurable variables with defaults
    resource_state: present

  tasks:
    - name: Validate inputs
      ansible.builtin.assert:
        that:
          - required_var is defined
        fail_msg: 'required_var must be defined'

    # Main tasks...

    - name: Verify completion
      ansible.builtin.debug:
        msg: 'Playbook completed successfully'
```
