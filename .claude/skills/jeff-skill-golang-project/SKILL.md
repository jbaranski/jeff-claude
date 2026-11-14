---
name: jeff-skill-golang-project
description: Configure or update Go projects with opinionated best practices using Go modules, golangci-lint, and built-in testing. Use when a repo should contain a Go project with modern tooling, idiomatic Go code, and 80% test coverage requirements.
---

This is an opinionated view for how Go projects should be configured and maintained.

## Rules

1. **Go modules**, idiomatic Go and Effective Go, minimal and deliberate dependencies.
2. **golangci-lint v2 only.** `.golangci.yml` starts with `version: '2'` (v2 rejects v1 configs outright). A `go install`
   path must contain `/v2/` — the v1 path silently installs v1.64.8, which can't read the config. CI uses
   `golangci-lint-action` v7+ (v6 and below run v1 only). A golangci-lint binary built with an older Go than `go.mod`
   targets refuses to run, so prefer the install script or `brew` over `go install`.
3. **Formatting runs through `golangci-lint fmt`** (gofmt + goimports configured as formatters) — no separate goimports
   install.
4. **Tests**: built-in `go test`, files alongside code (`handler.go` → `handler_test.go`), table-driven, run with
   `-race`, **80%+ coverage**.
5. **Use the Makefile targets**, not ad-hoc commands. Run `make check` (format check, lint, coverage gate, `govulncheck`) before calling
   work done; it reports and fails, it never rewrites — `make fmt` rewrites.
6. **CI**: workflow named `<project>-ci.yml`, `contents: read` only, checkout with `persist-credentials: false`, every action pinned to a commit SHA, the
   Dependabot guard on every job, `paths:` scoped to the module directory in a monorepo. CI never sends code, coverage,
   or test output to third-party services.
7. Never commit `vendor/` unless specifically required.
8. **Verify versions with WebSearch rather than guessing**; the versions below go stale.

Versions verified for this skill (November 2026) — keep golangci-lint, its action and Go in step:

| Tool                 | Version | Notes                                                                             |
| -------------------- | ------- | --------------------------------------------------------------------------------- |
| Go                   | 1.27.2  | 1.26.9 is the previous supported release                                          |
| golangci-lint        | v2.15.0 | v2 config schema — v1 configs are rejected outright                               |
| golangci-lint-action | v9      | v6 and below support golangci-lint v1 only                                        |
| govulncheck          | v1.9.0  | `go run golang.org/x/vuln/cmd/govulncheck@<version> ./...` in `make check` and CI |

## Layout

Applications put `main` packages under `cmd/<appname>/main.go` and private code under `internal/`; libraries keep their
packages at the root. Every project has `go.mod`, `go.sum`, `.golangci.yml`, `Makefile`, `README.md`, and
`.github/workflows/<project>-ci.yml` at the module root.

- `cmd/` - Main applications for this project
- `internal/` - Private application and library code (cannot be imported by other projects)
- `pkg/` - Library code that's ok to use by external applications (optional, use sparingly)

## References (read on demand)

| Read                                                           | When                                                                       |
| -------------------------------------------------------------- | -------------------------------------------------------------------------- |
| [references/setup.md](references/setup.md)                     | Installing Go, golangci-lint or bc; creating a new project; `.gitignore`   |
| [references/golangci-config.md](references/golangci-config.md) | Writing or changing `.golangci.yml`, or migrating a v1 config              |
| [references/makefile.md](references/makefile.md)               | Creating or changing the `Makefile` (test, coverage gate, lint, fmt, deps) |
| [references/github-actions.md](references/github-actions.md)   | Creating or changing the CI workflow                                       |

## Integration with Other Skills

- **jeff-skill-install-dependabot** — Set up Dependabot to keep Go module dependencies up to date
- **jeff-skill-dependabot-issue-resolution** — Resolve Dependabot PRs for Go module updates
