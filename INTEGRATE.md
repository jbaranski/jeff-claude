When asked to integrate these skills into a new repository, create a Makefile entry like this (create the Makefile if the repo doesn't already have one in project root).

Please note in the snippet "<the list of plugins the user asked for>" needs to be replaced with the actual plugin or plugins the user asked for.

```
.PHONY: sync-plugins

sync-plugins:
	@mkdir -p .claude/plugins
	@TMPDIR=$$(mktemp -d) && \
	  git clone --depth=1 https://github.com/jbaranski/jeff-claude.git $$TMPDIR && \
	  for plugin in <the list of plugins the user asked for>; do \
	    rm -rf .claude/plugins/$$plugin; \
	    cp -rL $$TMPDIR/plugins/$$plugin .claude/plugins/$$plugin 2>/dev/null || true; \
	    for skill_dir in .claude/plugins/$$plugin/skills/*/; do \
	      [ -d "$$skill_dir" ] || continue; \
	      skill=$$(basename $$skill_dir); \
	      if [ ! -f "$${skill_dir}SKILL.md" ] && [ -d "$$TMPDIR/.claude/skills/$$skill" ]; then \
	        rm -rf "$$skill_dir"; \
	        cp -r "$$TMPDIR/.claude/skills/$$skill" ".claude/plugins/$$plugin/skills/"; \
	      fi; \
	    done; \
	  done && \
	  rm -rf $$TMPDIR
	@echo "Plugins synced to .claude/plugins/"
```
