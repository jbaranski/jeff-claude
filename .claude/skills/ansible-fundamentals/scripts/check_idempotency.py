#!/usr/bin/env -S uv run --script --quiet
# /// script
# dependencies = ["pyyaml"]
# ///
"""Check Ansible playbooks and role task files for common idempotency issues.

Detects:
- command/shell tasks without changed_when or register
- shell tasks with pipes or redirects that don't set pipefail
- command tasks that use shell features (pipes, redirects, variables)
- tasks that look like they handle secrets but lack no_log
- tasks without a name
- short module names instead of FQCN

Accepts playbooks (a list of plays) and task files (a list of tasks, e.g. roles/*/tasks/*.yml).

Usage:
    check_idempotency.py playbooks/*.yml roles/*/tasks/*.yml
    check_idempotency.py --strict playbooks/site.yml
    check_idempotency.py --summary playbooks/*.yml

Exit status is 1 when any error or warning is found (or any info issue with --strict), else 0.
"""

import argparse
import sys
from pathlib import Path

import yaml

COMMAND_MODULES = {"command", "shell", "ansible.builtin.command", "ansible.builtin.shell"}
SECRET_MODULES = {
    "user",
    "ansible.builtin.user",
    "mysql_user",
    "community.mysql.mysql_user",
    "postgresql_user",
    "community.postgresql.postgresql_user",
}
SECRET_KEYWORDS = ("password", "passwd", "token", "secret", "api_key", "credential", "private_key")
SHORT_NAMES = {
    name: f"ansible.builtin.{name}"
    for name in (
        "apt",
        "assert",
        "command",
        "copy",
        "debug",
        "fail",
        "file",
        "get_url",
        "group",
        "lineinfile",
        "service",
        "set_fact",
        "shell",
        "systemd",
        "template",
        "uri",
        "user",
    )
}
PLAY_KEYS = {"hosts", "import_playbook", "ansible.builtin.import_playbook"}
TASK_SECTIONS = ("pre_tasks", "tasks", "post_tasks", "handlers")
BLOCK_SECTIONS = ("block", "rescue", "always")
READ_ONLY_WORDS = ("check", "verify", "test", "get", "find", "list", "show")


class Checker:
    def __init__(self, strict: bool) -> None:
        self.strict = strict
        self.issues: list[dict] = []

    def add(self, severity: str, location: str, message: str, suggestion: str) -> None:
        if severity == "info" and self.strict:
            severity = "warning"
        self.issues.append({"severity": severity, "location": location, "message": message, "suggestion": suggestion})

    def check_file(self, path: Path) -> list[dict]:
        self.issues = []
        try:
            content = yaml.safe_load(path.read_text())
        except yaml.YAMLError as err:
            return [{"severity": "error", "location": str(path), "message": f"Failed to parse YAML: {err}"}]
        except OSError as err:
            return [{"severity": "error", "location": str(path), "message": f"Failed to read file: {err}"}]

        if not isinstance(content, list):
            return []

        if any(isinstance(item, dict) and PLAY_KEYS & item.keys() for item in content):
            for play_idx, play in enumerate(content):
                if not isinstance(play, dict):
                    continue
                for section in TASK_SECTIONS:
                    self.check_tasks(play.get(section) or [], f"play[{play_idx}].{section}")
        else:
            self.check_tasks(content, "tasks")
        return self.issues

    def check_tasks(self, tasks: list, location: str) -> None:
        for idx, task in enumerate(tasks):
            if not isinstance(task, dict):
                continue
            loc = f"{location}[{idx}] ({task.get('name', 'unnamed')})"
            self.check_name(task, loc)
            self.check_command_shell(task, loc)
            self.check_secrets(task, loc)
            self.check_short_names(task, loc)
            for section in BLOCK_SECTIONS:
                if section in task:
                    self.check_tasks(task[section] or [], f"{location}[{idx}].{section}")

    def check_name(self, task: dict, loc: str) -> None:
        if "name" not in task and not any(k.endswith(("include_tasks", "import_tasks")) for k in task):
            self.add("warning", loc, "Task missing name", "Add a name starting with an uppercase action verb")

    def check_command_shell(self, task: dict, loc: str) -> None:
        module = next((k for k in task if k in COMMAND_MODULES), None)
        if module is None:
            return
        args = task[module]
        cmd = args.get("cmd", "") if isinstance(args, dict) else str(args or "")

        if "changed_when" not in task:
            name = str(task.get("name", "")).lower()
            if "register" not in task:
                self.add(
                    "warning",
                    loc,
                    "command/shell task without changed_when or register",
                    "Add register: and changed_when:",
                )
            elif any(word in name for word in READ_ONLY_WORDS):
                self.add("info", loc, "Read-only check without changed_when", "Add changed_when: false")
            else:
                self.add("warning", loc, "command/shell task without changed_when", "Add changed_when:")

        if module.endswith("shell") and any(c in cmd for c in "|>") and "pipefail" not in cmd:
            self.add(
                "warning",
                loc,
                "shell task with pipes or redirects but no pipefail",
                "Start the script with set -euo pipefail and set executable: /bin/bash",
            )

        if module.endswith("command") and any(c in cmd for c in ("|", ">", "<", "&&", ";", "$")):
            self.add(
                "info",
                loc,
                "command module used with shell syntax",
                "Use ansible.builtin.shell; command does not run a shell",
            )

    def check_secrets(self, task: dict, loc: str) -> None:
        if "no_log" in task:
            return
        has_secret_module = any(k in SECRET_MODULES for k in task)
        has_secret_arg = any(
            isinstance(value, dict) and any(kw in str(arg).lower() for arg in value for kw in SECRET_KEYWORDS)
            for value in task.values()
        )
        has_secret_text = any(kw in str(task).lower() for kw in SECRET_KEYWORDS)
        if has_secret_module or has_secret_arg or has_secret_text:
            self.add("warning", loc, "Task may handle secrets without no_log", "Add no_log: true")

    def check_short_names(self, task: dict, loc: str) -> None:
        for key in task:
            if key in SHORT_NAMES:
                self.add("info", loc, f"Short module name: {key}", f"Use {SHORT_NAMES[key]}")


def print_issues(path: Path, issues: list[dict]) -> None:
    if not issues:
        print(f"OK    {path}")
        return
    print(f"\n{path}")
    for severity in ("error", "warning", "info"):
        for issue in (i for i in issues if i["severity"] == severity):
            print(f"  {severity.upper():7} {issue['location']}: {issue['message']}")
            if issue.get("suggestion"):
                print(f"          -> {issue['suggestion']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", type=Path, help="Playbooks or task files to check")
    parser.add_argument("--strict", action="store_true", help="Treat info issues as warnings")
    parser.add_argument("--summary", action="store_true", help="Print only the summary")
    args = parser.parse_args()

    checker = Checker(strict=args.strict)
    failing = 0
    counts = {"error": 0, "warning": 0, "info": 0}
    for path in args.files:
        if not path.exists():
            print(f"ERROR   file not found: {path}", file=sys.stderr)
            counts["error"] += 1
            continue
        issues = checker.check_file(path)
        for issue in issues:
            counts[issue["severity"]] += 1
        if any(i["severity"] in ("error", "warning") for i in issues):
            failing += 1
        if not args.summary:
            print_issues(path, issues)

    print(
        f"\nChecked {len(args.files)} file(s): {counts['error']} errors, {counts['warning']} warnings, "
        f"{counts['info']} info; {failing} file(s) need attention"
    )
    return 1 if counts["error"] or counts["warning"] else 0


if __name__ == "__main__":
    sys.exit(main())
