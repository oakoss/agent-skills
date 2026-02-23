---
title: Task Patterns
description: Common mise task patterns for formatting, linting, testing, building, CI, benchmarking, release, and cleanup
tags:
  [
    tasks,
    fmt,
    lint,
    test,
    build,
    ci,
    bench,
    release,
    clean,
    patterns,
    pre-commit,
  ]
---

# Task Patterns

## Standard Task Set

A typical project defines these common tasks:

```toml
[tasks]
fmt = "prettier --write ."
"fmt:check" = "prettier --check ."
lint = "eslint src/"
"lint:fix" = "eslint src/ --fix"
test = "vitest run"
"test:watch" = "vitest"
"test:coverage" = "vitest run --coverage"
build = "tsc && vite build"
dev = "vite dev"
clean = "rm -rf dist node_modules/.cache"
```

## CI Pipeline Task

Compose tasks into a CI pipeline using dependencies:

```toml
[tasks.ci]
description = "Run full CI pipeline"
depends = ["fmt:check", "lint", "test", "build"]
```

Run the entire pipeline:

```bash
mise run ci
```

## Rust Project Tasks

```toml
[tools]
rust = "1.77"

[tasks]
fmt = "cargo fmt"
"fmt:check" = "cargo fmt --check"
lint = "cargo clippy -- -D warnings"
test = "cargo test"
build = "cargo build --release"
bench = "cargo bench"
clean = "cargo clean"

[tasks.ci]
depends = ["fmt:check", "lint", "test", "build"]
```

## Python Project Tasks

```toml
[tools]
python = "3.12"
"pipx:ruff" = "latest"
"pipx:mypy" = "latest"

[tasks]
fmt = "ruff format ."
"fmt:check" = "ruff format --check ."
lint = "ruff check . && mypy src/"
"lint:fix" = "ruff check --fix ."
test = "pytest -v"
"test:coverage" = "pytest --cov=src --cov-report=html"
clean = "rm -rf dist __pycache__ .pytest_cache .mypy_cache"

[tasks.ci]
depends = ["fmt:check", "lint", "test"]
```

## Go Project Tasks

```toml
[tools]
go = "1.22"
"go:mvdan.cc/gofumpt" = "latest"
"go:golang.org/x/lint/golint" = "latest"

[tasks]
fmt = "gofumpt -w ."
"fmt:check" = "gofumpt -d ."
lint = "go vet ./..."
test = "go test ./..."
"test:race" = "go test -race ./..."
build = "go build -o bin/app ./cmd/app"
bench = "go test -bench=. ./..."
clean = "rm -rf bin/"

[tasks.ci]
depends = ["fmt:check", "lint", "test:race", "build"]
```

## Node.js/TypeScript Project Tasks

```toml
[tools]
node = "22"
"npm:prettier" = "latest"
"npm:eslint" = "9"

[tasks]
fmt = "prettier --write ."
"fmt:check" = "prettier --check ."
lint = "eslint src/"
"lint:fix" = "eslint src/ --fix"
typecheck = "tsc --noEmit"
test = "vitest run"
"test:watch" = "vitest"
build = "vite build"
dev = "vite dev"
clean = "rm -rf dist .cache node_modules/.vite"

[tasks.ci]
depends = ["fmt:check", "lint", "typecheck", "test", "build"]
```

## Monorepo Tasks

```toml
[tasks."build:api"]
run = "npm run build"
dir = "apps/api"
sources = ["apps/api/src/**/*.ts"]
outputs = ["apps/api/dist/**/*.js"]

[tasks."build:web"]
run = "npm run build"
dir = "apps/web"
sources = ["apps/web/src/**/*.ts", "apps/web/src/**/*.tsx"]
outputs = ["apps/web/.next/**"]

[tasks.build]
depends = ["build:api", "build:web"]

[tasks."test:api"]
run = "npm test"
dir = "apps/api"

[tasks."test:web"]
run = "npm test"
dir = "apps/web"

[tasks.test]
depends = ["test:api", "test:web"]
```

## Release and Deploy Tasks

```toml
[tasks.release]
description = "Create a new release"
confirm = "Ready to create a release?"
run = """
#!/usr/bin/env bash
set -euo pipefail
VERSION=$(git describe --tags --abbrev=0 | awk -F. '{$NF = $NF + 1;} 1' | sed 's/ /./g')
git tag -a "$VERSION" -m "Release $VERSION"
git push origin "$VERSION"
echo "Released $VERSION"
"""

[tasks.deploy]
description = "Deploy to production"
depends = ["ci"]
confirm = "Deploy to production?"
run = "./scripts/deploy.sh"
env = { NODE_ENV = "production" }
```

## Pre-commit Hook Integration

Generate a git pre-commit hook that runs mise tasks:

```bash
mise generate git-pre-commit --write --task=pre-commit
```

```toml
[tasks.pre-commit]
description = "Pre-commit checks"
depends = ["fmt:check", "lint", "typecheck"]
```

## Database Tasks

```toml
[tasks."db:migrate"]
run = "npx prisma migrate dev"
description = "Run database migrations"

[tasks."db:seed"]
run = "npx prisma db seed"
depends = ["db:migrate"]

[tasks."db:reset"]
run = "npx prisma migrate reset --force"
confirm = "This will reset the database. Continue?"

[tasks."db:studio"]
run = "npx prisma studio"
description = "Open database GUI"
```
