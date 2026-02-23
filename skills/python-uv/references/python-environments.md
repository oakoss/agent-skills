---
title: Python Environments
description: Python version management, virtual environments, and interpreter configuration with uv
tags: [uv-python, python-version, venv, virtual-environment, python-pin]
---

# Python Environments

## Python Version Management

### Install Python Versions

```bash
uv python install 3.13

uv python install 3.11 3.12 3.13

uv python install pypy@3.10
```

### List Available Versions

```bash
uv python list

uv python list --only-installed
```

### Pin Project Python Version

```bash
uv python pin 3.12
```

Creates `.python-version`:

```text
3.12
```

### Upgrade to Latest Patch

```bash
uv python upgrade 3.12

uv python upgrade
```

### Find Python Interpreter

```bash
uv python find 3.12
```

## Virtual Environments

### Automatic Environment Management

uv creates and manages `.venv` automatically:

```bash
uv sync
```

This creates `.venv/` in the project root and installs all locked dependencies.

### Manual Virtual Environment Creation

```bash
uv venv

uv venv --python 3.12

uv venv .venv-test --python 3.11
```

### Using Specific Environment

```bash
UV_PROJECT_ENVIRONMENT=/path/to/venv uv sync
```

## Environment Behavior

### How uv run Works

```bash
uv run python app.py
```

This:

1. Finds the project `pyproject.toml`
2. Creates `.venv` if missing
3. Syncs dependencies if needed
4. Runs the command in the virtual environment

### No Manual Activation Needed

```bash
uv run pytest
uv run python -c "import sys; print(sys.version)"
uv run uvicorn app:app --reload
```

### Running with Extra Dependencies

```bash
uv run --extra postgres python -c "import psycopg"
```

## requires-python Configuration

### Minimum Version

```toml
[project]
requires-python = ">=3.12"
```

### Bounded Range

```toml
[project]
requires-python = ">=3.11,<3.14"
```

## Multi-Version Testing

```bash
uv python install 3.11 3.12 3.13

uv run --python 3.11 pytest
uv run --python 3.12 pytest
uv run --python 3.13 pytest
```

## .python-version vs requires-python

- `.python-version` sets the default Python for the project directory
- `requires-python` in `pyproject.toml` defines compatible Python range
- `uv python pin` writes `.python-version`
- `uv sync` respects `requires-python` for dependency resolution

## gitignore Configuration

```text
.venv/
__pycache__/
*.pyc
dist/
*.egg-info/
```
