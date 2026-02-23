---
title: Dependency Management
description: Adding, removing, and locking dependencies with uv, dependency groups, version constraints, and sources
tags: [uv-add, uv-remove, uv-lock, uv-sync, dependency-groups, sources]
---

# Dependency Management

## Adding Dependencies

```bash
uv add requests
uv add "requests>=2.31,<3"
uv add fastapi uvicorn
```

### Dev Dependencies

```bash
uv add --dev pytest ruff mypy
```

Adds to `[dependency-groups]`:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.8.0",
    "mypy>=1.13",
]
```

### Custom Groups

```bash
uv add --group docs mkdocs mkdocs-material
uv add --group test pytest pytest-cov pytest-asyncio
```

```toml
[dependency-groups]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.5",
]
test = [
    "pytest>=8.0",
    "pytest-cov>=6.0",
    "pytest-asyncio>=0.24",
]
```

### Optional Dependencies

```bash
uv add --optional postgres "psycopg[binary]>=3.0"
```

```toml
[project.optional-dependencies]
postgres = ["psycopg[binary]>=3.0"]
```

## Removing Dependencies

```bash
uv remove requests
uv remove --dev ruff
uv remove --group docs mkdocs
```

## Version Constraints

```bash
uv add "requests>=2.31"
uv add "requests>=2.31,<3"
uv add "requests~=2.31"
uv add "requests==2.31.0"
```

## Sources

Configure alternative package sources in `pyproject.toml`:

### Git Sources

```toml
[tool.uv.sources]
my-lib = { git = "https://github.com/org/my-lib", tag = "v1.0.0" }
```

### Local Path Sources

```toml
[tool.uv.sources]
my-lib = { path = "../my-lib", editable = true }
```

### Workspace Sources

```toml
[tool.uv.sources]
shared = { workspace = true }
```

### Index Sources

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
```

## Lockfile Management

### Create or Update Lockfile

```bash
uv lock
```

### Upgrade All Dependencies

```bash
uv lock --upgrade
```

### Upgrade Specific Package

```bash
uv lock --upgrade-package requests
```

### Verify Lockfile Currency

```bash
uv lock --check
```

## Syncing Environment

### Install All Dependencies

```bash
uv sync
```

### Skip Dev Dependencies

```bash
uv sync --no-dev
```

### Sync Specific Groups

```bash
uv sync --group docs
uv sync --all-groups
```

### Install with Optional Dependencies

```bash
uv sync --extra postgres
uv sync --all-extras
```

### CI/CD Sync Patterns

```bash
uv sync --locked

uv sync --frozen
```

### Force Reinstall

```bash
uv sync --reinstall
uv sync --reinstall-package requests
```

## Private Package Indexes

```toml
[[tool.uv.index]]
name = "private"
url = "https://pypi.company.com/simple/"

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

## Environment Markers

```toml
[project]
dependencies = [
    "uvloop>=0.21; sys_platform != 'win32'",
    "winloop>=0.1; sys_platform == 'win32'",
]
```

## Exporting Requirements

```bash
uv export --format requirements-txt > requirements.txt
uv export --format requirements-txt --no-dev > requirements.txt
```
