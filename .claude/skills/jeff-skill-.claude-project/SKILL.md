---
name: jeff-skill-.claude-project
description: Install Jeff's .claude configuration to the current repository. Use when asked to "configure Jeff's .claude configuration", "configure Jeff's .claude", or "setup Jeff's .claude" for the current project.
---

# Adding Jeff's .claude

This installs Jeff's preconfigured Claude skills and agents to be used consistently across all projects for a consistent AI experience with standardized agent and skill setups.

## Initial Setup

1. Run either scenario 1 or scenario 2, depending on which scenario you encounter:

- Scenario 1: No `.claude` directory exists.

  If the project root has no `.claude` directory, add the submodule:

  ```bash
  git submodule add https://github.com/jbaranski/jeff-claude.git .claude
  ```

- Scenario 2: Existing `.claude` directory exists

  If the project has an existing `.claude` directory, ensure \*.bak is in `.gitignore`, then run the following commands:

  ```bash
  # Add *.bak to .gitignore if not already present
  grep -q '^\*\.bak$' .gitignore 2>/dev/null || echo '*.bak' >> .gitignore

  # Backup existing config
  cp -r .claude .claude.bak

  # Remove from Git but don't commit
  git rm -rf .claude
  rm -rf .claude

  # Add submodule
  git submodule add https://github.com/jbaranski/jeff-claude.git .claude
  ```

2. After adding the submodule, configure `.gitmodules` to ignore local changes. The `git submodule add` command will create or update `.gitmodules` automatically. Then add the `ignore = dirty` setting:

```bash
git config -f .gitmodules submodule..claude.ignore dirty
```

## Updating Jeff's .claude configuration

1. To pull in the latest updates to Jeff's .claude configuration, run the following commands:

```bash
git submodule update --remote .claude
git add .claude
```
