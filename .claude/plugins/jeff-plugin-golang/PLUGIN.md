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

This plugin is distributed as a single zip (`jeff-plugin-golang.zip`). To install:

1. Extract the zip into your `.claude/plugins/` directory
2. Create symlinks for agent and skill discovery:
   ```bash
   # From your .claude directory
   cd .claude/agents
   ln -s ../plugins/jeff-plugin-golang/agents/jeff-agent-golang-code-reviewer.md
   ln -s ../plugins/jeff-plugin-golang/agents/jeff-agent-golang-software-developer.md

   cd ../skills
   ln -s ../plugins/jeff-plugin-golang/skills/jeff-skill-golang-project
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
