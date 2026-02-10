---
name: jeff-plugin-golang
description: Golang development plugin bundling agents and skills for idiomatic Go development, code review, and project configuration.
version: 1.0.0
agents:
  - jeff-agent-golang-code-reviewer
  - jeff-agent-golang-software-developer
skills:
  - jeff-skill-golang-project
---

# Golang Development Plugin

A self-contained plugin for Go development that bundles code review, software development, and project configuration capabilities.

## Contents

### Agents

| Agent | Description |
|-------|-------------|
| `jeff-agent-golang-code-reviewer` | Expert Go code reviewer focusing on idiomatic Go, error handling, concurrency, and Effective Go principles. |
| `jeff-agent-golang-software-developer` | Expert Go developer following idiomatic Go and Effective Go principles for development, testing, refactoring, and debugging. |

### Skills

| Skill | Description |
|-------|-------------|
| `jeff-skill-golang-project` | Configure or update Go projects with opinionated best practices using Go modules, golangci-lint, and built-in testing with 80% coverage requirements. |

## Installation

### From the marketplace (recommended)

```bash
curl -sL https://raw.githubusercontent.com/jbaranski/jeff-claude/main/install.sh | bash -s -- install jeff-plugin-golang
```

### Manual

1. Extract `jeff-plugin-golang.zip` into your `.claude/plugins/` directory
2. Copy agents and skills into the discovery directories:
   ```bash
   cp .claude/plugins/jeff-plugin-golang/agents/*.md .claude/agents/
   cp -r .claude/plugins/jeff-plugin-golang/skills/* .claude/skills/
   ```

## Directory Structure

```
jeff-plugin-golang/
├── PLUGIN.md
├── agents/
│   ├── jeff-agent-golang-code-reviewer.md
│   └── jeff-agent-golang-software-developer.md
└── skills/
    └── jeff-skill-golang-project/
        └── SKILL.md
```
