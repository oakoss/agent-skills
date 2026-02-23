---
title: Scripts and Tools
description: Running scripts with inline dependencies (PEP 723), ephemeral tool execution with uvx, and global tool management
tags: [uv-run, uvx, uv-tool, pep-723, inline-dependencies, scripts]
---

# Scripts and Tools

## Running Scripts

### Basic Script Execution

```bash
uv run python app.py

uv run python -m my_module
```

### Scripts with Inline Dependencies (PEP 723)

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
```

```bash
uv run script.py
```

uv resolves and installs inline dependencies automatically in an isolated environment.

### Initialize a Script

```bash
uv init --script example.py --python 3.12
```

### Add Dependencies to a Script

```bash
uv add --script example.py "requests<3" "rich"
```

### Lock Script Dependencies

```bash
uv lock --script example.py
```

### Shebang for Direct Execution

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///

import httpx

resp = httpx.get("https://example.com")
print(resp.status_code)
```

```bash
chmod +x script.py
./script.py
```

## Tool Management with uvx

### Ephemeral Tool Execution

```bash
uvx ruff check .
uvx black --check .
uvx mypy src/
uvx pycowsay "hello world"
```

Tools run in temporary environments and are cleaned up automatically.

### Specific Version

```bash
uvx ruff@0.8.0 check
uvx ruff@latest check
```

### Different Package and Command Names

```bash
uvx --from httpie http example.com
uvx --from jupyter-core jupyter
```

### Tools with Extras

```bash
uvx --from "mypy[faster-cache,reports]" mypy --xml-report report/
```

### Tools with Plugins

```bash
uvx --with mkdocs-material mkdocs build
uvx --with pytest-cov pytest --cov=src tests/
```

## Global Tool Installation

### Install Tools

```bash
uv tool install ruff
uv tool install "httpie>0.1.0"
uv tool install git+https://github.com/astral-sh/ruff
```

### Install with Additional Packages

```bash
uv tool install mkdocs --with mkdocs-material --with mkdocs-mermaid2-plugin
```

### Upgrade Tools

```bash
uv tool upgrade ruff
uv tool upgrade --all
```

### List Installed Tools

```bash
uv tool list
```

### Uninstall Tools

```bash
uv tool uninstall ruff
```

### Tool Install Directory

```bash
uv tool dir
```

## Common Tool Recipes

### Code Formatting

```bash
uvx ruff format .
uvx black .
uvx isort .
```

### Linting

```bash
uvx ruff check . --fix
uvx flake8 src/
uvx pylint src/
```

### Type Checking

```bash
uvx mypy src/
uvx pyright src/
```

### Security Scanning

```bash
uvx bandit -r src/
uvx pip-audit
```

### Documentation

```bash
uvx --with mkdocs-material mkdocs serve
uvx sphinx-build docs/ docs/_build/
```
