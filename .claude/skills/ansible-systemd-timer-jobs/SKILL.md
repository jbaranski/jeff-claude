---
name: ansible-systemd-timer-jobs
description: >
  Pattern for recurring jobs on Debian hosts: a shell script, a systemd oneshot service and a
  timer, all deployed by Ansible templates, with output written to syslog. Covers file layout,
  task and handler ordering, calendar versus interval timers, logging conventions, and
  validation before deploy.
when_to_use: >
  Use when adding a recurring job to a role (maintenance, certificate renewal, backups,
  polling an API for stats), writing a systemd timer or service with Ansible, or deciding
  between a systemd timer and cron.
---

# Scheduled Jobs as systemd Timers

Run recurring jobs as a script, a oneshot service and a timer, all templated by Ansible.
Prefer this to cron: systemd gives you ordering against other units, catch-up of missed runs,
per-run logs in the journal, and `systemctl list-timers` for visibility.

## The Three Files

| File               | Deployed to                                                                     | Purpose                         |
| ------------------ | ------------------------------------------------------------------------------- | ------------------------------- |
| `<job>.sh.j2`      | `/usr/local/bin/<job>` (or `/usr/local/sbin/` for root-only tools), mode `0755` | The work, plus its logging      |
| `<job>.service.j2` | `/etc/systemd/system/<job>.service`, mode `0644`                                | `Type=oneshot`, runs the script |
| `<job>.timer.j2`   | `/etc/systemd/system/<job>.timer`, mode `0644`                                  | Says when to run                |

Start every file with `# Managed by Ansible (roles/<role>) -- do not edit by hand.`

### Service

```ini
[Unit]
Description=<what the job does>
After=docker.service

[Service]
Type=oneshot
TimeoutStartSec=60
ExecStart=/usr/local/bin/<job>
```

- Order after what the job needs: `docker.service`, `postgresql.service` (with `Requires=` if
  it cannot run without it), `network-online.target` (with `Wants=`).
- A oneshot service has no default timeout. Set `TimeoutStartSec=` so a hung command cannot
  block the timer forever. Size it to the job: seconds for a poll, much longer for
  maintenance that legitimately runs for minutes.
- No `[Install]` section: the timer starts the service.
- Use an absolute path in `ExecStart`.

### Timer

Pick one shape.

| Shape    | Use for                              | Settings                                                |
| -------- | ------------------------------------ | ------------------------------------------------------- |
| Calendar | Maintenance at a time of day or week | `OnCalendar=`, `Persistent=true`, `RandomizedDelaySec=` |
| Interval | Polling or sampling                  | `OnBootSec=`, `OnUnitActiveSec=`                        |

```ini
# Calendar: weekly maintenance
[Timer]
OnCalendar=Sat 09:00:00 UTC
Persistent=true
RandomizedDelaySec=5min

[Install]
WantedBy=timers.target
```

```ini
# Interval: run every 5 minutes, first run 5 minutes after boot
[Timer]
OnBootSec=5min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

- `Persistent=true` makes a calendar timer catch up a run missed while the host was off. It
  has no effect on interval timers, so do not add it there.
- Use `RandomizedDelaySec=` on calendar timers so many hosts or jobs do not fire at once.
- Put the schedule or interval in the role's `defaults/main.yml`, template it into the timer,
  and comment why that value was chosen.

## Ansible Tasks

Order matters: write the files, reload systemd, then enable the timer. Define the two
handlers inside the role, because handlers do not cross roles.

```yaml
- name: Create <job> script
  ansible.builtin.template:
    src: <job>.sh.j2
    dest: /usr/local/bin/<job>
    owner: root
    group: root
    mode: '0755'

- name: Create <job> systemd service
  ansible.builtin.template:
    src: <job>.service.j2
    dest: /etc/systemd/system/<job>.service
    owner: root
    group: root
    mode: '0644'
  notify: Reload systemd

- name: Create <job> systemd timer
  ansible.builtin.template:
    src: <job>.timer.j2
    dest: /etc/systemd/system/<job>.timer
    owner: root
    group: root
    mode: '0644'
  notify:
    - Reload systemd
    - Restart <job> timer

- name: Reload systemd before enabling the timer
  ansible.builtin.meta: flush_handlers

- name: Ensure the <job> timer is enabled and started
  ansible.builtin.systemd_service:
    name: <job>.timer
    enabled: true
    state: started
```

```yaml
# handlers/main.yml
- name: Reload systemd
  ansible.builtin.systemd_service:
    daemon_reload: true

- name: Restart <job> timer
  ansible.builtin.systemd_service:
    name: <job>.timer
    state: restarted
```

`meta: flush_handlers` runs every handler queued so far in the play, not only the two above.
If the role has other pending handlers (for example a service restart), place the flush
where running them at that point is acceptable, and say so in a comment.

## Script Conventions

```bash
#!/bin/bash
# Managed by Ansible (roles/<role>) -- do not edit by hand.
# <one line on what it does and how often it runs>
set -euo pipefail

LOG_TAG="<job>"
```

- Write to syslog with `logger -t "${LOG_TAG}" "message"`, tagging every line with the job
  name. Output printed to stdout or stderr is captured by systemd into the journal, but
  explicit `logger` lines have a stable tag and do not depend on how the unit is run.
- Log the start of any step that changes state, every failure, and the outcome (for
  example `Rotated 3 files, freed 1.2G`).
- Failures: `logger -t "${LOG_TAG}" "ERROR: <short reason>"`, then `exit 1`. `set -e` alone
  exits with no log line, which leaves a silent gap, and a non-zero exit marks the unit
  failed in systemd.
- One line per message. Each line is a separate log record, so do not print multi-line
  blobs. `logger` truncates at 1 KiB by default; raise it with `-S <bytes>` for longer
  lines.
- For metrics or any data someone will query, emit compact JSON (`jq -c`) shaped for
  querying: flat keys, one object per entity (per disk, per container, per queue), with
  the entity's name as a value (`"disk":"sda"`) and not as a key
  (`"disks":{"sda":{...}}`), so adding an entity adds rows, not columns. Include a
  `kind` field when one run writes different shapes, make field names unique across kinds,
  and keep each field the same type on every line (a number stays a number; use `null` for
  missing, never a string). Whatever collects the logs can then turn each key into a column.
- Never log secrets, passwords or tokens.
- Make the job safe to run twice. A calendar timer with `Persistent=true` can fire right
  after boot, so wait for whatever the job depends on (a container, a socket, the network)
  instead of failing.

### Syslog timestamps must be ISO

Anything that parses a syslog line by position (a collector pattern that expects
`<timestamp> <host> <tag>: <message>`) requires rsyslog's **ISO timestamp format**, where the
timestamp is one word with no spaces:

```text
2026-10-12T00:05:03.123456+00:00 myhost <job>: message     <- required
Oct 12 01:32:43 myhost <job>: message                      <- traditional: a bug
```

The traditional format has a three-word timestamp, so a pattern anchored to the tag position
does not match it. The line still arrives, unparsed, and **nothing reports an error**. A host
that logs in the traditional format is a bug and must be fixed, not worked around or
accepted: set rsyslog's file output to the ISO template (`RSYSLOG_FileFormat`, not
`RSYSLOG_TraditionalFileFormat`) and confirm it on the host.

Check every host that runs a job, or that a parser reads logs from. This should print `0`:

```bash
grep -cvE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T' /var/log/syslog
```

### Jinja collisions

Shell and `jq` code can contain `{{`, `{%` or `{#`, which Jinja will try to render. Wrap
the affected block in `{% raw %}...{% endraw %}`, or ship it as a plain file with
`ansible.builtin.copy` if it needs no variables.

### Numbers from APIs

APIs often return numbers as strings (`"2.9"`) or with units (`"1.12%"`). Convert them in
`jq` (`rtrimstr("%") | tonumber`) so downstream tools can compare and chart them, and make
the filter tolerant of missing keys (emit `null`, never crash).

## Validation Before Deploy

| Check            | How                                                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| Script syntax    | `bash -n` on the rendered script; `shellcheck` if installed                                                           |
| Unit files       | `systemd-analyze verify` on the rendered files, if available                                                          |
| Templates render | Render with Ansible's `template` module in a throwaway local play (`-c local -i localhost,`)                          |
| Playbook         | `uv run ansible-playbook --syntax-check playbooks/<playbook>.yml`                                                     |
| Filter logic     | Run the `jq` program on a saved sample of the real API response and on edge cases (missing keys, empty objects, null) |
| Failure paths    | Run the script with stub commands that fail, and confirm the `ERROR:` line and exit code                              |

If `ansible.cfg` loads callback plugins with side effects, render and test with an empty
`ANSIBLE_CONFIG` so they never run.

After deploy, on the host:

```bash
systemctl list-timers '<job>*'
journalctl -u <job>.service -n 30 --no-pager
journalctl -t <job> -n 30 --no-pager
```

Ansible also logs its own module calls to syslog, and they mention the unit name, so a bare
search for the job name in `/var/log/syslog` matches deploy noise. Search for the tag
(`<job>:`) and exclude `ansible-`. Do not start a job that changes production state
(a backup, a service restart) just to test its logging.

## Checklist for a New Job

1. Script, service and timer templates with the managed header.
2. Schedule or interval in `defaults/main.yml`, with a comment.
3. The five tasks and two handlers above, in the same role.
4. `logger -t <job>` for start, outcome and errors; `ERROR:` prefix; non-zero exit on failure.
5. `TimeoutStartSec=` sized to the job.
6. Local validation from the table.
7. After deploy, the job's log lines appear under its tag.
8. If a parser reads the job's lines by position, the host's syslog uses ISO timestamps (see
   "Syslog timestamps must be ISO").
9. Note how to query the job's logs wherever your team keeps such notes.

## Related Skills

- **ansible-role-design** - Where tasks, handlers, templates and defaults live
- **ansible-idempotency** - Keeping the deploy tasks and the job itself idempotent
- **ansible-fundamentals** - FQCN, `uv run`, and module selection
