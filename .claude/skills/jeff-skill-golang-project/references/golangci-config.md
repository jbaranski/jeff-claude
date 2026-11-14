# golangci-lint v2 Configuration

Comprehensive linting configuration. This is **golangci-lint v2 schema** — the v2 binary rejects a v1
config outright with `unsupported version of the configuration`, so the `version` key is mandatory.

```yaml
version: '2'

run:
  tests: true

linters:
  # `default: standard` already enables errcheck, govet, ineffassign, staticcheck
  # and unused. Everything listed below is in addition to those five.
  default: standard
  enable:
    - bodyclose # Check HTTP response body is closed
    - dupl # Code clone detection
    - exhaustive # Check exhaustiveness of enum switch statements
    - gocritic # Highly extensible Go linter
    - gocyclo # Computes cyclomatic complexity
    - godot # Check if comments end in a period
    - goprintffuncname # Check printf-like function names
    - gosec # Inspect source code for security problems
    - misspell # Finds commonly misspelled English words
    - nilerr # Finds code that returns nil even if it checks that error is not nil
    - nolintlint # Reports ill-formed or insufficient nolint directives
    - prealloc # Find slice declarations that could potentially be preallocated
    - revive # Fast, configurable, extensible, flexible, and beautiful linter for Go
    - unconvert # Remove unnecessary type conversions
    - unparam # Find unused function parameters
  settings:
    gocyclo:
      min-complexity: 15
    dupl:
      threshold: 100
    gocritic:
      enabled-tags:
        - diagnostic
        - performance
        - style
    revive:
      rules:
        - name: var-naming
        - name: exported
        - name: indent-error-flow
  exclusions:
    generated: lax
    paths:
      - vendor

issues:
  max-same-issues: 0
  max-issues-per-linter: 0

formatters:
  enable:
    - gofmt # Check whether code was gofmt-ed
    - goimports # Check import statements are formatted
  settings:
    gofmt:
      simplify: true
  exclusions:
    paths:
      - vendor
```

Verify the config parses before relying on it:

```bash
golangci-lint config verify
```

### What changed from the v1 config, and why

The linter coverage is unchanged — the v1 file listed 24 linters, and this one enables the same
checks. Four names disappeared from `linters.enable` without losing anything:

| v1                                                          | v2                              | Reason                                                                                           |
| ----------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------ |
| `gosimple`, `stylecheck`                                    | folded into `staticcheck`       | Both were removed as separate linters; `staticcheck` in v2 runs the `S*` and `ST*` checks itself |
| `gofmt`, `goimports`                                        | top-level `formatters:` section | v2 separates formatters from linters                                                             |
| `errcheck`, `govet`, `ineffassign`, `staticcheck`, `unused` | implied by `default: standard`  | These five are the standard set; listing them is redundant                                       |

Other schema moves:

| v1                           | v2                                                                                     |
| ---------------------------- | -------------------------------------------------------------------------------------- |
| (no version key)             | `version: '2'` — required                                                              |
| `run.skip-dirs`              | `linters.exclusions.paths` (and `formatters.exclusions.paths`)                         |
| `linters-settings:`          | `linters.settings:`                                                                    |
| `issues.exclude-use-default` | `linters.exclusions.presets` — omitting `presets` is the equivalent of the old `false` |
| `run.timeout`                | dropped — v2 has no timeout by default                                                 |

`issues.max-same-issues` and `issues.max-issues-per-linter` are unchanged.

### Migrating an existing v1 config

Do not hand-convert. golangci-lint v2 ships a migrator:

```bash
golangci-lint migrate          # rewrites .golangci.yml, backs the original up to .golangci.bck.yml
golangci-lint config verify    # confirm the result parses
```

Two caveats:

- `migrate` validates the input against the **v1** JSON schema first, so a config carrying keys that
  were already removed late in v1's life fails before migration starts. `run.skip-dirs` is the common
  one — rename it to `issues.exclude-dirs` (its v1 replacement) and re-run, or pass `--skip-validation`.
- Comments are not carried over; the migrator warns about this. Re-add them afterwards.
