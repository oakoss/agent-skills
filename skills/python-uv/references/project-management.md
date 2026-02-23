---
title: Project Management
description: Initializing projects, pyproject.toml configuration, build systems, and project structure
tags: [uv-init, pyproject, build-system, project-structure, src-layout]
---

# Project Management

## Initialize a Project

```bash
uv init my-project
cd my-project
```

Creates:

```text
my-project/
  pyproject.toml
  .python-version
  hello.py
```

### Application vs Library

```bash
uv init my-app

uv init --lib my-lib
```

Library layout uses `src/` structure with `py.typed` marker:

```text
my-lib/
  pyproject.toml
  src/
    my_lib/
      __init__.py
      py.typed
```

### Init with Specific Python Version

```bash
uv init --python 3.12 my-project
```

## pyproject.toml Configuration

### Application

```toml
[project]
name = "my-app"
version = "0.1.0"
description = "My application"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.8.0",
    "mypy>=1.13",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Library

```toml
[project]
name = "my-lib"
version = "0.1.0"
description = "My library"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0",
]
readme = "README.md"
license = { text = "MIT" }
authors = [
    { name = "Author", email = "author@example.com" },
]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]

[project.urls]
Homepage = "https://github.com/org/my-lib"
Documentation = "https://my-lib.readthedocs.io"

[project.optional-dependencies]
postgres = ["psycopg[binary]>=3.0"]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Build System Options

### Hatchling (default)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### uv Build Backend

```toml
[build-system]
requires = ["uv_build>=0.10.4,<0.11.0"]
build-backend = "uv_build"
```

### Setuptools

```toml
[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.build_meta"
```

## Entry Points

### Console Scripts

```toml
[project.scripts]
my-cli = "my_app.cli:main"
```

```bash
uv run my-cli
```

### GUI Scripts

```toml
[project.gui-scripts]
my-gui = "my_app.gui:main"
```

## Tool Configuration in pyproject.toml

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
strict = true
python_version = "3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

## uv-Specific Configuration

```toml
[tool.uv]
dev-dependencies = ["pytest>=8.0"]

[tool.uv.sources]
my-lib = { path = "../my-lib" }
```

## Project Commands

```bash
uv run python -m my_app

uv run pytest

uv run ruff check .

uv run mypy src/
```
