---
title: Workspaces
description: Monorepo support with uv workspaces, multi-package projects, and cross-package dependencies
tags: [workspace, monorepo, multi-package, uv-workspace, members]
---

# Workspaces

## Workspace Structure

```text
my-monorepo/
  pyproject.toml          # Root workspace config
  uv.lock                 # Single lockfile for all packages
  packages/
    shared/
      pyproject.toml
      src/shared/
        __init__.py
    api/
      pyproject.toml
      src/api/
        __init__.py
    worker/
      pyproject.toml
      src/worker/
        __init__.py
```

## Root pyproject.toml

```toml
[project]
name = "my-monorepo"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.uv.workspace]
members = ["packages/*"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Exclude Members

```toml
[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/experimental"]
```

## Member pyproject.toml

### Shared Library

```toml
[project]
name = "shared"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### API Service (depends on shared)

```toml
[project]
name = "api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
    "shared",
]

[tool.uv.sources]
shared = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Worker Service (depends on shared)

```toml
[project]
name = "worker"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "celery>=5.4",
    "shared",
]

[tool.uv.sources]
shared = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Workspace Commands

### Lock All Packages

```bash
uv lock
```

A single `uv.lock` at the workspace root covers all members.

### Sync Specific Package

```bash
uv sync --package api
uv sync --package worker
```

### Run in Specific Package

```bash
uv run --package api uvicorn api:app --reload
uv run --package worker celery -A worker.tasks worker
uv run --package shared pytest
```

### Build Specific Package

```bash
uv build --package shared
uv build --package api
```

## Workspace Dependency Resolution

All workspace members share a single lockfile. Dependencies are resolved together, preventing version conflicts across packages.

```toml
[tool.uv.sources]
shared = { workspace = true }
```

The `workspace = true` source tells uv to resolve the dependency from the workspace rather than PyPI.

## Development Workflow

### Adding Dependencies to a Member

```bash
cd packages/api
uv add httpx
```

Or from the root:

```bash
uv add --package api httpx
```

### Running Tests Across Workspace

```bash
uv run --package shared pytest
uv run --package api pytest
uv run --package worker pytest
```

### Shared Dev Dependencies at Root

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.8.0",
    "mypy>=1.13",
]
```

Root dev dependencies are available to all workspace members when synced.
