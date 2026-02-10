#!/usr/bin/env bash
set -euo pipefail

REPO="jbaranski/jeff-claude"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
MARKETPLACE_URL="${RAW_BASE}/marketplace.json"

usage() {
  cat <<EOF
Jeff's Claude Code Plugin Marketplace Installer

Usage:
  install.sh list                     List available plugins
  install.sh install <plugin-name>    Install a plugin into the current project
  install.sh uninstall <plugin-name>  Uninstall a plugin from the current project

Examples:
  # List all available plugins
  curl -sL ${RAW_BASE}/install.sh | bash -s -- list

  # Install the Go plugin into your project
  curl -sL ${RAW_BASE}/install.sh | bash -s -- install jeff-plugin-golang

  # Or run locally
  ./install.sh install jeff-plugin-golang
EOF
  exit 1
}

require_commands() {
  for cmd in curl jq unzip; do
    if ! command -v "$cmd" &>/dev/null; then
      echo "Error: '$cmd' is required but not installed."
      exit 1
    fi
  done
}

fetch_marketplace() {
  curl -sL "$MARKETPLACE_URL"
}

cmd_list() {
  local marketplace
  marketplace=$(fetch_marketplace)

  echo "Available plugins:"
  echo ""
  echo "$marketplace" | jq -r '
    .plugins | to_entries[] |
    "  \(.key)\n    \(.value.description)\n    version: \(.value.version)\n    agents:  \(.value.agents | length)\n    skills:  \(.value.skills | length)\n"
  '
}

cmd_install() {
  local plugin_name="$1"
  local marketplace
  marketplace=$(fetch_marketplace)

  # Validate plugin exists
  local plugin
  plugin=$(echo "$marketplace" | jq -r ".plugins[\"${plugin_name}\"] // empty")
  if [ -z "$plugin" ]; then
    echo "Error: Plugin '${plugin_name}' not found."
    echo ""
    echo "Available plugins:"
    echo "$marketplace" | jq -r '.plugins | keys[]' | sed 's/^/  /'
    exit 1
  fi

  local zip_path
  zip_path=$(echo "$plugin" | jq -r '.zip')
  local zip_url="${RAW_BASE}/${zip_path}"

  echo "Installing plugin: ${plugin_name}"

  # Create directories
  mkdir -p ".claude/plugins/${plugin_name}" ".claude/agents" ".claude/skills"

  # Download and extract
  local tmp_zip
  tmp_zip=$(mktemp /tmp/${plugin_name}-XXXXXX.zip)
  echo "  Downloading ${zip_url}..."
  curl -sL "$zip_url" -o "$tmp_zip"
  echo "  Extracting to .claude/plugins/${plugin_name}/"
  unzip -qo "$tmp_zip" -d ".claude/plugins/${plugin_name}/"
  rm -f "$tmp_zip"

  # Copy agents into .claude/agents/
  echo "$plugin" | jq -r '.agents[].file' | while read -r agent_file; do
    local agent_basename
    agent_basename=$(basename "$agent_file")
    local src=".claude/plugins/${plugin_name}/${agent_file}"
    local dest=".claude/agents/${agent_basename}"
    cp -f "$src" "$dest"
    echo "  Installed agent: ${agent_basename}"
  done

  # Copy skills into .claude/skills/
  echo "$plugin" | jq -r '.skills[].dir' | while read -r skill_dir; do
    local skill_basename
    skill_basename=$(basename "$skill_dir")
    local src=".claude/plugins/${plugin_name}/${skill_dir}"
    local dest=".claude/skills/${skill_basename}"
    rm -rf "$dest"
    cp -rf "$src" "$dest"
    echo "  Installed skill: ${skill_basename}"
  done

  echo ""
  echo "Plugin '${plugin_name}' installed successfully."
}

cmd_uninstall() {
  local plugin_name="$1"
  local plugin_dir=".claude/plugins/${plugin_name}"

  if [ ! -d "$plugin_dir" ]; then
    echo "Error: Plugin '${plugin_name}' is not installed."
    exit 1
  fi

  echo "Uninstalling plugin: ${plugin_name}"

  # Use marketplace.json from the plugin itself if available, otherwise fetch
  local plugin_meta=""
  if [ -f "$plugin_dir/PLUGIN.md" ]; then
    # Parse agents and skills from the installed plugin directory
    for agent_file in "$plugin_dir"/agents/*.md; do
      if [ -f "$agent_file" ]; then
        local agent_basename
        agent_basename=$(basename "$agent_file")
        rm -f ".claude/agents/${agent_basename}"
        echo "  Removed agent: ${agent_basename}"
      fi
    done

    for skill_dir_entry in "$plugin_dir"/skills/*/; do
      if [ -d "$skill_dir_entry" ]; then
        local skill_basename
        skill_basename=$(basename "$skill_dir_entry")
        rm -rf ".claude/skills/${skill_basename}"
        echo "  Removed skill: ${skill_basename}"
      fi
    done
  fi

  # Remove plugin directory
  rm -rf "$plugin_dir"
  echo ""
  echo "Plugin '${plugin_name}' uninstalled."
}

# --- Main ---
require_commands

case "${1:-}" in
  list)
    cmd_list
    ;;
  install)
    [ -z "${2:-}" ] && usage
    cmd_install "$2"
    ;;
  uninstall)
    [ -z "${2:-}" ] && usage
    cmd_uninstall "$2"
    ;;
  *)
    usage
    ;;
esac
