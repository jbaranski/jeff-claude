When asked to integrate these plugins into a repository, add this `sync-plugins` target to the project-root `Makefile` (create the Makefile if there isn't one), replacing `<plugins>` with the space-separated plugin names the user asked for (e.g. `jeff-plugin-angular jeff-plugin-aws-solution-architect`). Then run `make sync-plugins`.

```
.PHONY: sync-plugins

PLUGINS := <plugins>

sync-plugins:
	@mkdir -p .claude/agents .claude/skills
	@TMPDIR=$$(mktemp -d) && \
	  trap 'rm -rf "$$TMPDIR"' EXIT && \
	  git clone --quiet --depth=1 https://github.com/jbaranski/jeff-claude.git "$$TMPDIR" && \
	  for plugin in $(PLUGINS); do \
	    src="$$TMPDIR/plugins/$$plugin"; \
	    if [ ! -d "$$src" ]; then echo "Unknown plugin: $$plugin" >&2; exit 1; fi; \
	    for agent in "$$src"/agents/*.md; do \
	      [ -e "$$agent" ] || continue; \
	      cp -L "$$agent" .claude/agents/; \
	    done; \
	    for skill in "$$src"/skills/*; do \
	      [ -e "$$skill" ] || continue; \
	      rm -rf ".claude/skills/$$(basename "$$skill")"; \
	      cp -RL "$$skill" .claude/skills/; \
	    done; \
	  done
	@echo "Synced agents to .claude/agents/ and skills to .claude/skills/"
```

Agents land in `.claude/agents/` and skills in `.claude/skills/` — the folders Claude Code loads for every session in the repo, including cloud sessions, under their own names (`jeff-angular-software-developer`, `jeff-skill-angular-project`). Don't sync into `.claude/plugins/`: Claude Code never reads a project's `.claude/plugins/` folder. If an earlier version of this target created one, delete it.

`cp -L` copies the files the repo's symlinks point to, so the synced agents and skills are real files. Commit them. Re-run the target to pick up updates; it overwrites each synced agent and replaces each synced skill directory, so don't hand-edit those files.
