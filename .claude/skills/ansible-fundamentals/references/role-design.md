# Ansible Role Design

Patterns derived from geerlingguy's production roles, narrowed to Debian targets.

## Standard Directory Structure

```text
role-name/
├── defaults/
│   └── main.yml          # User-configurable defaults (lowest precedence)
├── vars/
│   └── main.yml          # Internal constants
├── tasks/
│   ├── main.yml          # Task router
│   ├── install.yml       # Feature-specific tasks
│   └── configure.yml
├── handlers/
│   └── main.yml          # Event-triggered tasks
├── templates/
│   └── config.conf.j2    # Jinja2 templates
├── files/
│   └── static-file.txt   # Static files
├── meta/
│   └── main.yml          # Role metadata, dependencies
└── README.md             # Documentation
```

### Directory Purposes

| Directory    | Purpose                     | Precedence |
| ------------ | --------------------------- | ---------- |
| `defaults/`  | User-overridable values     | Lowest     |
| `vars/`      | Internal/OS-specific values | High       |
| `tasks/`     | Ansible tasks               | N/A        |
| `handlers/`  | Service restarts, reloads   | N/A        |
| `templates/` | Jinja2 config files         | N/A        |
| `files/`     | Static files to copy        | N/A        |
| `meta/`      | Galaxy info, dependencies   | N/A        |

### When to Omit Directories

Only create directories that are actually needed:

- **Omit `templates/`** if using only `lineinfile` or `copy`
- **Omit `handlers/`** if role doesn't manage services
- **Omit `vars/`** if there are no internal constants
- **Omit `files/`** if no static files to copy

## Task Organization

### Main Task File as Router

Use `tasks/main.yml` as a routing file that includes feature-specific files:

```yaml
# tasks/main.yml
---
- name: Install packages
  ansible.builtin.include_tasks: install.yml

- name: Configure service
  ansible.builtin.include_tasks: configure.yml

- name: Setup users
  ansible.builtin.include_tasks: users.yml
  when: role_users | length > 0
```

### When to Split Tasks

| Scenario          | Approach                   |
| ----------------- | -------------------------- |
| < 30 lines        | Keep in main.yml           |
| 30-100 lines      | Consider splitting         |
| > 100 lines       | Definitely split           |
| Optional features | Separate file with `when:` |

### Task File Naming

Use descriptive, feature-based names:

```text
tasks/
├── main.yml              # Router only
├── install.yml           # Package installation
├── configure.yml         # Configuration tasks
└── users.yml             # User management
```

## Variable Organization

### defaults/ vs vars/

| Location            | Purpose            | User Override?           |
| ------------------- | ------------------ | ------------------------ |
| `defaults/main.yml` | User configuration | Yes (easily)             |
| `vars/main.yml`     | Internal constants | Possible but discouraged |

### defaults/main.yml Example

```yaml
# defaults/main.yml
---
# User-configurable options
docker_edition: 'ce'
docker_service_state: started
docker_service_enabled: true
docker_users: []

# Feature toggles
docker_install_compose_plugin: true
```

### vars/main.yml Example

```yaml
# vars/main.yml
---
# Internal values (not for user override)
docker_packages:
  - docker-ce
  - docker-ce-cli
  - containerd.io
docker_config_path: /etc/docker/daemon.json
```

If a second OS family ever appears, add `vars/<os_family>.yml` and load it with
`ansible.builtin.include_vars: "{{ ansible_facts['os_family'] }}.yml"`.

## Variable Naming Convention

Prefix variables with role name:

```yaml
# Pattern: {role_name}_{feature}_{attribute}

# Examples
docker_edition: 'ce'
docker_service_state: started
docker_users: []

# Grouped by feature
security_ssh_port: 22
security_ssh_password_auth: 'no'
security_fail2ban_enabled: true
```

## Handler Patterns

### Simple Handler Definitions

```yaml
# handlers/main.yml
---
- name: Restart docker
  ansible.builtin.systemd_service:
    name: docker
    state: restarted

- name: Reload nginx
  ansible.builtin.systemd_service:
    name: nginx
    state: reloaded
```

### Handler Naming

Short, capitalized action + service (ansible-lint `name[casing]` requires the capital), and
`notify` must match exactly:

```yaml
- name: Restart ssh
- name: Reload nginx
- name: Reload systemd # daemon-reload
```

Handlers are scoped to the role that defines them; a role can't notify another role's handler
reliably, so define what you notify.

### Throttled Handlers

For cluster operations, restart one node at a time:

```yaml
- name: Restart postgresql
  ansible.builtin.systemd_service:
    name: postgresql
    state: restarted
  throttle: 1
```

## Template Organization

### When to Use Templates

Use `templates/` when:

- Configuration has conditional content
- Need variable substitution
- Complex multi-line configuration
- Users may need to extend/override

Use `lineinfile` when:

- Simple single-line changes
- Modifying existing system files

### Template Variables

Expose template paths as variables for user override:

```yaml
# defaults/main.yml
nginx_conf_template: nginx.conf.j2
nginx_vhost_template: vhost.j2
```

```yaml
# tasks/configure.yml
- name: Deploy nginx config
  ansible.builtin.template:
    src: '{{ nginx_conf_template }}'
    dest: /etc/nginx/nginx.conf
  notify: Reload nginx
```

## Meta Configuration

### meta/main.yml Structure

```yaml
# meta/main.yml
---
galaxy_info:
  author: your_name
  description: Role description
  license: MIT
  min_ansible_version: '2.21'
  platforms:
    - name: Debian
      versions:
        - bookworm
        - trixie

dependencies:
  - role: common
  - role: geerlingguy.docker
    when: install_docker | default(false)
```

## Role Complexity Scaling

Based on geerlingguy role analysis:

| Role Complexity | Directories | Task Files   | Examples          |
| --------------- | ----------- | ------------ | ----------------- |
| Minimal         | 3-4         | 1 (main.yml) | pip, git          |
| Standard        | 5-6         | 2-4          | security, docker  |
| Complex         | 7+          | 5-8          | postgresql, nginx |

Create only the directories a role actually uses.

### Minimal Role

```text
pip/
├── defaults/main.yml
├── tasks/main.yml
├── meta/main.yml
└── README.md
```

### Standard Role

```text
docker/
├── defaults/main.yml
├── vars/main.yml
├── tasks/{main,install,configure}.yml
├── handlers/main.yml
├── meta/main.yml
└── README.md
```

### Complex Role

```text
postgresql/
├── defaults/main.yml
├── vars/main.yml
├── tasks/{main,install,configure,users,databases}.yml
├── handlers/main.yml
├── templates/{postgresql.conf,pg_hba.conf}.j2
├── meta/main.yml
└── README.md
```

## File Validation

Validate critical configuration files:

```yaml
- name: Update SSH configuration
  ansible.builtin.lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^PermitRootLogin'
    line: 'PermitRootLogin no'
    validate: 'sshd -T -f %s'
  notify: Restart ssh

- name: Update sudoers
  ansible.builtin.lineinfile:
    path: /etc/sudoers
    line: '{{ user }} ALL=(ALL) NOPASSWD: ALL'
    validate: 'visudo -cf %s'
```

## Documentation

Every role needs a README.md with:

1. **Description** - What the role does
2. **Requirements** - Prerequisites
3. **Role Variables** - All variables with defaults
4. **Dependencies** - Other roles needed
5. **Example Playbook** - How to use it
