---
name: jeff-skill-marketplace-install
description: Install, uninstall, or list plugins from Jeff's Claude Code Plugin Marketplace. Use when asked to "install a plugin", "list plugins", "add golang plugin", or "remove a plugin".
---

This skill manages plugins from Jeff's Claude Code Plugin Marketplace hosted at `jbaranski/jeff-claude` on GitHub.

## Prerequisites

The following CLI tools must be available:

- `curl` - for downloading from GitHub
- `jq` - for parsing marketplace.json
- `unzip` - for extracting plugin zips

Verify: `command -v curl jq unzip`

## Marketplace URL

```
https://raw.githubusercontent.com/jbaranski/jeff-claude/main/marketplace.json
```

## Commands

### List available plugins

Run the install script with `list`:

```bash
curl -sL https://raw.githubusercontent.com/jbaranski/jeff-claude/main/install.sh | bash -s -- list
```

### Install a plugin

Run from the **root of the target project**:

```bash
curl -sL https://raw.githubusercontent.com/jbaranski/jeff-claude/main/install.sh | bash -s -- install <plugin-name>
```

Example:

```bash
curl -sL https://raw.githubusercontent.com/jbaranski/jeff-claude/main/install.sh | bash -s -- install jeff-plugin-golang
```

This will:

1. Download the plugin zip from the marketplace
2. Extract it to `.claude/plugins/<plugin-name>/`
3. Create symlinks in `.claude/agents/` and `.claude/skills/` for discovery

### Uninstall a plugin

```bash
curl -sL https://raw.githubusercontent.com/jbaranski/jeff-claude/main/install.sh | bash -s -- uninstall <plugin-name>
```

This will:

1. Remove agent and skill symlinks that point to the plugin
2. Delete the `.claude/plugins/<plugin-name>/` directory

## Workflow

1. When the user asks to install a plugin, first run `list` to show available options
2. Confirm the plugin name with the user if ambiguous
3. Run the `install` command from the project root
4. Verify the installation by checking that symlinks exist and resolve correctly

## After Installation

After installing a plugin, the user may need to restart Claude Code for the new agents and skills to be discovered.
