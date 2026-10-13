When asked to integrate these plugins into a repository, add this `sync-plugins` target to the project-root `Makefile` (create the Makefile if there isn't one), replacing `<plugins>` with the space-separated plugin names the user asked for (e.g. `jeff-plugin-angular jeff-plugin-aws-solution-architect`). Then run `make sync-plugins`.

```
.PHONY: sync-plugins

sync-plugins:
	@mkdir -p .claude/plugins
	@TMPDIR=$$(mktemp -d) && \
	  trap 'rm -rf "$$TMPDIR"' EXIT && \
	  git clone --quiet --depth=1 https://github.com/jbaranski/jeff-claude.git "$$TMPDIR" && \
	  for plugin in <plugins>; do \
	    if [ ! -d "$$TMPDIR/plugins/$$plugin" ]; then echo "Unknown plugin: $$plugin" >&2; exit 1; fi; \
	    rm -rf ".claude/plugins/$$plugin"; \
	    cp -RL "$$TMPDIR/plugins/$$plugin" ".claude/plugins/$$plugin"; \
	  done
	@echo "Plugins synced to .claude/plugins/"
```

`cp -RL` dereferences the repo's symlinks, so each synced plugin contains real copies of its agents and skills. Re-run the target to pick up updates; it replaces each plugin directory wholesale, so don't hand-edit files under `.claude/plugins/`.
