# GitHub Actions

Create `.github/workflows/<project>-ci.yml` for continuous integration.

Name the file after the project (e.g. `web-ci.yml`, `api-ci.yml`) rather than a generic `ci.yml`, so several projects in one repo each get their own workflow instead of overwriting each other.

**Scope triggers to the Go module's directory.** If this module lives at the repo root, omit `paths:` entirely — every change in the repo is relevant. If it shares a monorepo with other stacks (e.g. a `web/` frontend next to a `golang/` service, or `infra/`), scope `paths:` to the module directory so an unrelated change (a README edit, a frontend-only change) doesn't trigger a Go build. Always include the workflow file itself in `paths:` so edits to the CI config are still validated.

**Skip Dependabot-triggered runs.** Every job carries the Dependabot guard from `jeff-skill-install-dependabot` so Dependabot PRs and pushes don't consume Actions minutes. If you add a job, give it the same `if:`. If a job already has an `if:` condition, combine it with the guard using `&&` rather than replacing it, wrapping the existing condition in parentheses (e.g. `if: (existing-condition) && github.actor != 'dependabot[bot]' && ...`).

**Run steps in the module directory.** `defaults.run.working-directory` makes every `run:` step execute inside `<module-dir>`, where `go.mod` lives. Omit the `defaults:` block entirely if the module is at the repo root. It does not apply to `uses:` steps, which is why the setup-go cache path below is spelled out relative to the repo root.

**Least privilege.** The workflow grants only `contents: read`, and checkout uses `persist-credentials: false` so the token is not left in `.git/config` for later steps.

```yaml
name: <project>-ci

on:
  push:
    branches: [main]
    paths:
      - '<module-dir>/**' # e.g. 'golang/**' — omit this whole `paths:` key if the module is at repo root
      - '.github/workflows/<project>-ci.yml'
  pull_request:
    branches: [main]
    paths:
      - '<module-dir>/**'
      - '.github/workflows/<project>-ci.yml'

permissions:
  contents: read

jobs:
  test:
    name: Test
    if: github.actor != 'dependabot[bot]' && github.event.pull_request.user.login != 'dependabot[bot]'
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: <module-dir> # e.g. 'golang' — omit this whole `defaults:` block if the module is at repo root
    steps:
      - name: Check out code
        uses: actions/checkout@v7
        with:
          persist-credentials: false

      - name: Set up Go
        uses: actions/setup-go@v7
        with:
          go-version-file: <module-dir>/go.mod # 'go.mod' if the module is at repo root
          cache: true
          # A module with no dependencies has no go.sum; setup-go then warns and skips caching.
          # Key on <module-dir>/go.mod instead for such modules.
          cache-dependency-path: <module-dir>/go.sum # 'go.sum' if the module is at repo root

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
