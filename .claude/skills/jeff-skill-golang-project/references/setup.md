# Go Project Setup

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
   - Verify rather than guess; versions in this skill go stale.

   Versions verified for the examples in this skill (October 2026):

   | Tool                 | Version | Notes                                                                                       |
   | -------------------- | ------- | ------------------------------------------------------------------------------------------- |
   | Go                   | 1.27.2  | 1.26.9 is the previous supported release                                                    |
   | golangci-lint        | v2.14.0 | v2 config schema — v1 configs are rejected outright; released binaries built with Go 1.27.0 |
   | golangci-lint-action | v9      | v6 and below support golangci-lint v1 only                                                  |

   Keep these three in step. `golangci-lint-action` v6 cannot run golangci-lint v2, and a
   golangci-lint binary built with an older Go than your `go.mod` targets refuses to run.

## go.mod

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

## Initialize Project

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

## .gitignore

Add `.gitignore` with common Go exclusions:

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
