# Makefile

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
