# Modules, Collections and Commands

## Module Selection Guide

### Decision Matrix

| Need                | Use                                  | Why                              |
| ------------------- | ------------------------------------ | -------------------------------- |
| Install packages    | `ansible.builtin.apt/yum/dnf`        | Native modules handle state      |
| Manage files        | `ansible.builtin.copy/template/file` | Idempotent by default            |
| Edit config lines   | `ansible.builtin.lineinfile`         | Surgical edits, not full replace |
| Run commands        | `ansible.builtin.command`            | When no native module exists     |
| Need shell features | `ansible.builtin.shell`              | Pipes, redirects, globs          |
| Manage services     | `ansible.builtin.systemd_service`    | State management built-in        |
| Manage users        | `ansible.builtin.user`               | Cross-platform, idempotent       |

### Prefer Native Modules

Native modules provide:

- Built-in idempotency (no need for `changed_when`)
- Better error handling
- Cross-platform compatibility
- Clear documentation

```yaml
# PREFER native module
- name: Create user
  ansible.builtin.user:
    name: deploy
    groups: docker
    state: present

# AVOID command when module exists
- name: Create user
  ansible.builtin.command: useradd -G docker deploy
  # Requires: changed_when, failed_when, idempotency logic
```

### When Command/Shell is Acceptable

Use `command` or `shell` modules when:

1. No native module exists for the operation
2. Interacting with vendor CLI tools (certbot, kubectl, aws)
3. Running one-off scripts

Add proper controls:

```yaml
- name: Enable Apache module
  ansible.builtin.command: a2enmod {{ module_name }}
  register: mod_result
  changed_when: "'already enabled' not in mod_result.stdout"
  failed_when:
    - mod_result.rc != 0
    - "'already enabled' not in mod_result.stdout"
```

## Collections in Use

| Collection          | Purpose            | Example Modules                |
| ------------------- | ------------------ | ------------------------------ |
| `ansible.builtin`   | Core functionality | copy, template, command, user  |
| `ansible.posix`     | POSIX systems      | authorized_key, synchronize    |
| `community.general` | General utilities  | interfaces_file, ini_file      |
| `community.docker`  | Docker management  | docker_container, docker_image |

### Installing Collections

```bash
# Install from requirements
uv run ansible-galaxy collection install -r requirements.yml

# Install specific collection
uv run ansible-galaxy collection install community.docker
```

## Common Execution Patterns

### Running Playbooks

```bash
# Basic execution
uv run ansible-playbook playbooks/my-playbook.yml

# With extra variables
uv run ansible-playbook playbooks/deploy.yml \
  -e "app_version=1.4.2"

# Limit to specific hosts
uv run ansible-playbook playbooks/update.yml --limit webservers

# Check mode (dry run)
uv run ansible-playbook playbooks/deploy.yml --check --diff

# With tags
uv run ansible-playbook playbooks/setup.yml --tags "network,storage"
```

### Linting

```bash
# Run ansible-lint
uv run ansible-lint
```

### Diagnostic Commands

```bash
# Check syntax without running
uv run ansible-playbook --syntax-check playbooks/my-playbook.yml

# List hosts in inventory
uv run ansible-inventory --list

# Test connection to all hosts
uv run ansible all -m ping
```

## Task Naming Conventions

Use descriptive names with action verbs:

| Verb      | Use When                     |
| --------- | ---------------------------- |
| Ensure    | Verifying state exists       |
| Configure | Modifying settings           |
| Install   | Adding packages              |
| Create    | Making new resources         |
| Remove    | Deleting resources           |
| Deploy    | Releasing applications       |
| Update    | Modifying existing resources |

Examples:

```yaml
- name: Ensure Docker is installed
- name: Configure SSH security settings
- name: Create admin user account
- name: Deploy application configuration
```
