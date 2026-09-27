---
name: jeff-skill-golang-project
description: Configure or update Go projects with opinionated best practices using Go modules, golangci-lint, and built-in testing. Use when a repo should contain a Go project with modern tooling, idiomatic Go code, and 80% test coverage requirements.
---

This is an opinionated view for how Go projects should be configured and maintained.

## Prerequisites

Before proceeding:

1. Check if Go is installed by running `go version`.
   - If not installed on macOS: `brew install go`
   - If not installed on Linux: Download from https://go.dev/dl/
   - Verify installation: `go version`
2. Install golangci-lint (**v2** — see the version note below):
   - macOS: `brew install golangci-lint`
   - Linux: `curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin v2.14.0`
   - Verify: `golangci-lint --version` — the output **must** start with `golangci-lint has version 2.`

   If you prefer `go install`, the module path must contain `/v2/`:

   ```bash
   go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.14.0
   ```

   The v1 path (`github.com/golangci/golangci-lint/cmd/golangci-lint@latest`) still resolves — it
   silently installs **v1.64.8**, which cannot read the v2 config below. Prefer the install script or
   `brew`: `go install` builds golangci-lint with whatever Go toolchain resolves locally, and a binary
   built with an older Go than your module targets fails with
   `the Go language version (go1.X) used to build golangci-lint is lower than the targeted Go version`.
   The released binaries are built with the current Go.

3. Install bc (basic calculator) for coverage threshold checks:
   - macOS: `brew install bc`
   - Linux (Ubuntu/Debian): `sudo apt-get install bc`
   - Linux (RHEL/CentOS): `sudo yum install bc`
   - Verify: `bc --version`
4. Use WebSearch to verify current versions:
   - "Go golang latest stable version [current-year]"
   - "golangci-lint latest version [current-year]"
   - "golangci-lint-action latest version"
   - Update all version numbers in examples below with verified versions
   - Ensure Go is updated to the latest stable version if needed
   - DO NOT skip this step. DO NOT guess at version numbers.

   Versions verified for the examples in this skill (September 2026):

   | Tool                 | Version | Notes                                                                                       |
   | -------------------- | ------- | ------------------------------------------------------------------------------------------- |
   | Go                   | 1.27.1  | 1.26.8 is the previous supported release                                                    |
   | golangci-lint        | v2.14.0 | v2 config schema — v1 configs are rejected outright; released binaries built with Go 1.27.0 |
   | golangci-lint-action | v9      | v6 and below support golangci-lint v1 only                                                  |

   Keep these three in step. `golangci-lint-action` v6 cannot run golangci-lint v2, and a
   golangci-lint binary built with an older Go than your `go.mod` targets refuses to run.

## Goals

- Use Go modules for dependency management
- Follow idiomatic Go and Effective Go principles
- Use golangci-lint for comprehensive linting
- Use built-in Go testing with 80%+ code coverage
- Keep dependencies minimal and deliberate
- Make test/lint/build repeatable and auditable

## Required Layout

### Project Structure

For applications (with main package):

```
project-root/
├── cmd/
│   └── appname/
│       └── main.go
├── internal/
│   ├── handler/
│   │   ├── handler.go
│   │   └── handler_test.go
│   └── service/
│       ├── service.go
│       └── service_test.go
├── go.mod
├── go.sum
├── .golangci.yml
├── Makefile
├── README.md
└── .github/
    └── workflows/
        └── ci.yml
```

For libraries (no main package):

```
project-root/
├── example.go
├── example_test.go
├── go.mod
├── go.sum
├── .golangci.yml
├── Makefile
├── README.md
└── .github/
    └── workflows/
        └── ci.yml
```

### Directory Conventions

- `cmd/` - Main applications for this project
- `internal/` - Private application and library code (cannot be imported by other projects)
- `pkg/` - Library code that's ok to use by external applications (optional, use sparingly)

## Configuration Files

### go.mod

Initialize with Go modules:

```bash
go mod init github.com/username/projectname
```

This creates a `go.mod` file:

```go
module github.com/username/projectname

go 1.27

require (
    // Dependencies will be added here automatically
)
```

### .golangci.yml

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

#### What changed from the v1 config, and why

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

#### Migrating an existing v1 config

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

### Makefile

Common commands for consistency:

```makefile
.PHONY: all test build clean lint lint-config fmt fmt-check coverage coverage-check tidy check deps

# Default target
all: fmt lint test build

# Run tests
test:
	go test -v -race ./...

# Run tests with coverage
coverage:
	go test -v -race -coverprofile=coverage.out -covermode=atomic ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"
	@go tool cover -func=coverage.out | grep total | awk '{print "Total coverage: " $$3}'

# Check if coverage meets minimum threshold (80%)
coverage-check:
	@go test -race -coverprofile=coverage.out -covermode=atomic ./... > /dev/null
	@COVERAGE=$$(go tool cover -func=coverage.out | grep total | awk '{print $$3}' | sed 's/%//'); \
	if [ $$(echo "$$COVERAGE < 80" | bc -l) -eq 1 ]; then \
		echo "Coverage $$COVERAGE% is below minimum 80%"; \
		exit 1; \
	else \
		echo "Coverage $$COVERAGE% meets minimum 80%"; \
	fi

# Build the application
build:
	go build -v ./...

# Format code (runs the formatters configured in .golangci.yml: gofmt + goimports)
fmt:
	golangci-lint fmt

# Check formatting without rewriting files (non-zero exit if anything would change)
fmt-check:
	golangci-lint fmt --diff

# Run linters
lint:
	golangci-lint run ./...

# Verify .golangci.yml parses against the v2 schema
lint-config:
	golangci-lint config verify

# Clean build artifacts
clean:
	go clean
	rm -f coverage.out coverage.html

# Tidy dependencies
tidy:
	go mod tidy
	go mod verify

# Run all checks (format check, lint, test with coverage check)
# NOTE: this is a gate, not a fixer — it depends on `fmt-check`, which reports
# misformatted code and exits non-zero without rewriting anything. Use `make fmt`
# (or `make all`) when you want files reformatted in place.
check: fmt-check lint coverage-check

# Install development dependencies
# NOTE: the v2 module path contains /v2/. Installing
# github.com/golangci/golangci-lint/cmd/golangci-lint (no /v2/) silently gets v1,
# which cannot read the v2 .golangci.yml. A separate goimports install is no longer
# needed — `golangci-lint fmt` runs it as a configured formatter.
GOLANGCI_LINT_VERSION ?= v2.14.0

deps:
	curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh \
		| sh -s -- -b $$(go env GOPATH)/bin $(GOLANGCI_LINT_VERSION)
	golangci-lint --version
```

## Project Setup Commands

### Initialize Project

1. Create project directory: `mkdir project-name && cd project-name`
2. Initialize Go module: `go mod init github.com/username/project-name`
3. Create project structure:
   ```bash
   mkdir -p cmd/appname internal
   touch cmd/appname/main.go
   ```
4. Create `.golangci.yml` with configuration above
5. Create `Makefile` with commands above
6. Initialize git: `git init`

### Common Commands

Use the Makefile for consistency:

```bash
# Format code
make fmt

# Check formatting without rewriting
make fmt-check

# Run linters
make lint

# Verify .golangci.yml against the v2 schema
make lint-config

# Run tests
make test

# Run tests with coverage report
make coverage

# Run tests and check 80% coverage threshold
make coverage-check

# Build the application
make build

# Run all checks (format check, lint, coverage check) — fails on misformatted
# code instead of reformatting it
make check

# Clean artifacts
make clean

# Tidy dependencies
make tidy
```

## Testing Requirements

- Use built-in `go test` for all tests
- Tests must live alongside code (e.g., `handler.go` → `handler_test.go`)
- Minimum 80% code coverage required
- Use table-driven tests (idiomatic Go pattern)
- Run tests with race detector: `go test -race`

### Example Test (Table-Driven)

```go
// internal/calculator/calculator.go
package calculator

func Add(a, b int) int {
    return a + b
}

func Divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}
```

```go
// internal/calculator/calculator_test.go
package calculator

import (
    "testing"
)

func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a        int
        b        int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -2, -3, -5},
        {"zero", 0, 0, 0},
        {"mixed", -5, 10, 5},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}

func TestDivide(t *testing.T) {
    tests := []struct {
        name      string
        a         int
        b         int
        expected  int
        expectErr bool
    }{
        {"valid division", 10, 2, 5, false},
        {"division by zero", 10, 0, 0, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Divide(tt.a, tt.b)
            if tt.expectErr {
                if err == nil {
                    t.Errorf("Divide(%d, %d) expected error, got nil", tt.a, tt.b)
                }
            } else {
                if err != nil {
                    t.Errorf("Divide(%d, %d) unexpected error: %v", tt.a, tt.b, err)
                }
                if result != tt.expected {
                    t.Errorf("Divide(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
                }
            }
        })
    }
}
```

## Code Quality Standards

- All code must pass `golangci-lint run` with no errors
- All code must be formatted with `gofmt` and `goimports`
- Follow Effective Go: https://go.dev/doc/effective_go
- Follow Go Code Review Comments: https://go.dev/wiki/CodeReviewComments
- Use meaningful variable names (avoid single-letter unless idiomatic: `i`, `j`, `k` for loops)
- Handle errors explicitly (no ignored errors)
- Document exported functions, types, and packages

## GitHub Actions

Create `.github/workflows/ci.yml` for continuous integration.

**Scope triggers to the Go module's directory.** If this module lives at the repo root, omit `paths:` entirely — every change in the repo is relevant. If it shares a monorepo with other stacks (e.g. a `web/` frontend next to a `golang/` service, or `infra/`), scope `paths:` to the module directory so an unrelated change (a README edit, a frontend-only change) doesn't trigger a Go build. Always include the workflow file itself in `paths:` so edits to the CI config are still validated.

```yaml
name: jeff-skill-golang-project

on:
  push:
    branches: [main]
    paths:
      - '<module-dir>/**' # e.g. 'golang/**' — omit this whole `paths:` key if the module is at repo root
      - '.github/workflows/ci.yml'
  pull_request:
    branches: [main]
    paths:
      - '<module-dir>/**'
      - '.github/workflows/ci.yml'

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.27'
          cache: true

      - name: Download dependencies
        run: go mod download

      - name: Verify dependencies
        run: go mod verify

      # golangci-lint-action v6 and below only support golangci-lint v1 and cannot
      # read the v2 config. v7+ are the v2-compatible releases; v9 is current.
      # install-only lets the same binary drive both the format check and the lint run.
      - name: Install golangci-lint
        uses: golangci/golangci-lint-action@v9
        with:
          version: v2.14.0
          install-only: true

      - name: Format check
        run: golangci-lint fmt --diff

      - name: Verify lint config
        run: golangci-lint config verify

      - name: Run golangci-lint
        run: golangci-lint run ./...

      - name: Run tests with coverage
        run: go test -v -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Check coverage threshold
        run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
          echo "Total coverage: $COVERAGE%"
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage $COVERAGE% is below minimum 80%"
            exit 1
          fi
```

## Best Practices

- Keep dependencies minimal - only add what you truly need
- Use `go mod tidy` regularly to clean up unused dependencies
- Never commit `vendor/` directory unless specifically required
- Use context for cancellation and timeouts in long-running operations
- Prefer `errors.New()` or `fmt.Errorf()` for error creation
- Use error wrapping with `%w` for error context: `fmt.Errorf("failed to process: %w", err)`
- Write idiomatic Go - simple and readable over clever
- CI must not send code, coverage, or test output to third-party services — coverage is enforced locally by the 80% threshold step
- Add `.gitignore` with common Go exclusions:

  ```
  # Binaries
  *.exe
  *.exe~
  *.dll
  *.so
  *.dylib
  *.test

  # Output and coverage
  *.out
  coverage.html
  coverage.out

  # Go workspace file
  go.work
  go.work.sum

  # IDE
  .idea/
  .vscode/*
  !.vscode/launch.json
  *.swp
  *.swo
  *~

  # OS
  .DS_Store
  Thumbs.db
  ```

## Idiomatic Go Patterns

- Use short variable names in small scopes
- Error handling: Check errors explicitly, don't ignore them
- Use defer for cleanup (closing files, unlocking mutexes)
- Accept interfaces, return structs
- Keep interfaces small (prefer many small interfaces over large ones)
- Use goroutines and channels for concurrent operations
- Use `sync.WaitGroup` for waiting on multiple goroutines
- Avoid global state and init() functions when possible

## Integration with Other Skills

- **jeff-skill-install-dependabot** — Set up Dependabot to keep Go module dependencies up to date
- **jeff-skill-dependabot-issue-resolution** — Resolve Dependabot PRs for Go module updates
