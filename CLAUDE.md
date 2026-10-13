# CLAUDE.md — jeff-claude Repo Guide

This repo contains Claude Code plugins, agents, and skills for personal use. Read this entire file before making any changes.

---

## Naming Conventions

| Thing            | Pattern                       | Example                                   |
| ---------------- | ----------------------------- | ----------------------------------------- |
| Agent file       | `jeff-agent-{tech}-{role}.md` | `jeff-agent-phaser-software-developer.md` |
| Agent `name`     | `jeff-{tech}-{role}`          | `jeff-phaser-software-developer`          |
| Skill directory  | `jeff-skill-{tech}-{what}`    | `jeff-skill-phaser-gamedev`               |
| Skill entry file | `SKILL.md` inside skill dir   | `jeff-skill-phaser-gamedev/SKILL.md`      |
| Plugin directory | `jeff-plugin-{tech}`          | `jeff-plugin-phaser`                      |

---

## Adding a New Plugin — Exact Checklist

Work through every item before committing. Missing any one of these caused multiple rounds of rework.

### 1. Create canonical agent files in `.claude/agents/`

- Filename: `jeff-agent-{tech}-software-developer.md` and `jeff-agent-{tech}-code-reviewer.md`
- Each file has YAML frontmatter with `name`, `description`, and `skills` list
- `name` in frontmatter is `jeff-{tech}-{role}` — the filename without the `agent-` segment. This is the name users invoke, so don't change existing ones
- List only skills that actually exist in `.claude/skills/`, and symlink every listed skill into the plugin (step 3)
- Write only what the model wouldn't do by default: your opinions, thresholds, tool choices, and gotchas. Don't restate language tutorials or generic best practices
- Every skill in an agent's `skills:` list is loaded **in full** into the agent's context each time it starts. Keep the list short — usually one core skill — and keep that SKILL.md small
- Agents don't set `model:`; they inherit the session's model

### 2. Create canonical skill directory in `.claude/skills/`

- Directory name: `jeff-skill-{tech}-{what}` (`shell-bash` and `ansible-fundamentals` predate this convention; leave them as they are)
- Must contain `SKILL.md` with frontmatter `name: jeff-skill-{tech}-{what}`
- Keep `SKILL.md` to the rules that apply to every task; put detailed patterns in `references/*.md` and link each from a "read when..." table in SKILL.md so they load only when needed (see `ansible-fundamentals`)
- Write the `description` as what the skill covers plus when to use it — it's the only part always in context, and it decides when the skill loads
- `name` in SKILL.md frontmatter must match the directory name exactly

### 3. Create the plugin directory under `plugins/`

```
plugins/jeff-plugin-{tech}/
  .claude-plugin/
    plugin.json
  agents/
    jeff-agent-{tech}-software-developer.md  ← symlink
    jeff-agent-{tech}-code-reviewer.md       ← symlink
  skills/
    jeff-skill-{tech}-{what}                 ← symlink
    jeff-skill-install-nodejs                ← symlink (if agents need it)
    jeff-skill-install-prettier              ← symlink (if agents need it)
    jeff-skill-typescript-project            ← symlink (if agents need it)
    jeff-skill-install-dependabot            ← symlink (if agents need it)
```

**Every entry in `agents/` and `skills/` MUST be a relative symlink.** Never create real files or directories there.

Symlink targets use relative paths:

- Agents: `../../../.claude/agents/{filename}.md`
- Skills: `../../../.claude/skills/{skill-dir-name}`

Create symlinks with:

```bash
ln -s ../../../.claude/agents/jeff-agent-{tech}-software-developer.md plugins/jeff-plugin-{tech}/agents/jeff-agent-{tech}-software-developer.md
ln -s ../../../.claude/skills/jeff-skill-{tech}-{what} plugins/jeff-plugin-{tech}/skills/jeff-skill-{tech}-{what}
```

### 4. Create `plugin.json`

Bump `version` whenever a plugin's agents or skills change (minor for additions/fixes, major when a skill or agent is renamed or removed) — installed plugins are cached per version.

```json
{
  "name": "jeff-plugin-{tech}",
  "description": "...",
  "version": "1.0.0",
  "author": {
    "name": "Jeff Baranski"
  }
}
```

### 5. Register in `.claude-plugin/marketplace.json`

Add an entry to the `plugins` array:

```json
{
  "name": "jeff-plugin-{tech}",
  "source": "./plugins/jeff-plugin-{tech}",
  "description": "..."
}
```

### 6. Update `README`

- Add an inspiration link under the `Inspired by` section if the skill content came from an external source
- Add `/plugin install jeff-plugin-{tech}@jeff-plugins` to the install commands list

### 7. Run Prettier on all new files

```bash
npx prettier --write .claude/agents/jeff-agent-{tech}-*.md .claude/skills/jeff-skill-{tech}-{what}/
npx prettier --check .claude/agents/jeff-agent-{tech}-*.md .claude/skills/jeff-skill-{tech}-{what}/
```

Prettier config is in `.prettierrc.json` (printWidth: 120, singleQuote). The Makefile has `prettier-fix` and `prettier-check` targets.

### 8. Do NOT create zips manually

The `zip/` directory is auto-populated by the GitHub Actions workflow `.github/workflows/package-skills.yml` on every push to `main`. Never create, edit, or commit zip files manually.

---

## Mistakes Made When Adding jeff-plugin-phaser (Do Not Repeat)

These were real errors made during implementation — documented so future sessions don't repeat them.

### Mistake 1: Wrong naming — didn't follow existing conventions

Named the skill `phaser-gamedev` instead of `jeff-skill-phaser-gamedev` and the agent `jeff-agent-phaser-gamedev` instead of `jeff-agent-phaser-software-developer`. **Before writing a single file, look at existing agents and skills in `.claude/agents/` and `.claude/skills/` and match the pattern exactly.**

### Mistake 2: Created real files in `plugins/` instead of symlinks

Put actual `.md` files and a real directory in `plugins/jeff-plugin-phaser/agents/` and `plugins/jeff-plugin-phaser/skills/`. **All entries in a plugin's `agents/` and `skills/` directories are always relative symlinks — never real files.** Verify with `ls -la` before committing.

### Mistake 3: Missing `plugin.json`

Forgot to create `plugins/jeff-plugin-phaser/.claude-plugin/plugin.json`. Every plugin needs this file.

### Mistake 4: Missing marketplace.json registration

Forgot to add the new plugin to `.claude-plugin/marketplace.json`. The plugin won't be discoverable without this.

### Mistake 5: Forgot to update README

Forgot both the inspiration link and the `/plugin install` command in `README`. The README is the user-facing install reference — always update it.

### Mistake 6: Manually created zip files

Created zip files by hand in `zip/`. CI generates these automatically. Manual zips add noise and may conflict with CI output. Never touch the `zip/` directory.

### Mistake 7: Didn't run Prettier before committing

All 7 new phaser markdown files failed `prettier --check`. Run `npx prettier --write` on all new files before staging them, then verify with `--check`.

---

## Pre-Commit Checklist

Before committing any new plugin work:

- [ ] Agent files are in `.claude/agents/` with correct frontmatter and naming
- [ ] Skill directory is in `.claude/skills/` with `SKILL.md` and correct frontmatter
- [ ] Plugin directory exists under `plugins/jeff-plugin-{tech}/`
- [ ] `plugin.json` exists at `plugins/jeff-plugin-{tech}/.claude-plugin/plugin.json`
- [ ] All entries in `plugins/.../agents/` are symlinks (`ls -la` to verify)
- [ ] All entries in `plugins/.../skills/` are symlinks (`ls -la` to verify)
- [ ] Every skill in each agent's `skills:` list is symlinked into that plugin's `skills/`
- [ ] `.claude-plugin/marketplace.json` has the new plugin entry
- [ ] `README` has the inspiration link (if applicable) and install command
- [ ] `npx prettier --check` passes on all new/modified files
- [ ] No zip files created or modified manually
