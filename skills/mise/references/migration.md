---
title: Migration
description: Migrating to mise from asdf, nvm, pyenv, Makefiles, and other tool managers
tags:
  [
    migration,
    asdf,
    nvm,
    pyenv,
    rbenv,
    direnv,
    makefile,
    comparison,
    alternatives,
  ]
---

# Migration

## From asdf

Mise is a drop-in replacement for asdf with full `.tool-versions` compatibility.

### Direct Compatibility

Mise reads `.tool-versions` files natively:

```text
node 22.11.0
python 3.12.1
ruby 3.3.0
```

No changes needed to start using mise with existing asdf projects.

### Migration to mise.toml

Convert `.tool-versions` to `mise.toml` for access to tasks, env, and backends:

```bash
# Before (.tool-versions)
# node 22.11.0
# python 3.12.1

# After (mise.toml) - use mise to generate
mise use node@22.11.0
mise use python@3.12.1
```

Resulting `mise.toml`:

```toml
[tools]
node = "22.11.0"
python = "3.12.1"
```

### Key Differences from asdf

| Feature        | asdf                | mise                                         |
| -------------- | ------------------- | -------------------------------------------- |
| Config format  | `.tool-versions`    | `mise.toml` (also reads `.tool-versions`)    |
| Task runner    | None                | Built-in `[tasks]`                           |
| Env management | None (use direnv)   | Built-in `[env]` section                     |
| Speed          | Shell-based plugins | Native Rust, parallel installs               |
| Backends       | Plugins only        | Core + npm, cargo, pipx, GitHub, Go          |
| Fuzzy versions | No                  | Yes (`node = "22"` resolves to latest 22.x)  |
| Legacy files   | Via plugins         | Built-in (`.nvmrc`, `.python-version`, etc.) |

### Plugin Compatibility

Mise uses the same plugin system as asdf. Existing asdf plugins work with mise:

```bash
# asdf plugins work in mise
mise plugins install terraform
mise use terraform@1.7
```

## From nvm

Replace nvm with mise for Node.js version management:

```bash
# nvm (before)
# .nvmrc contains: 22
nvm install
nvm use

# mise (after)
mise use node@22
```

Mise reads `.nvmrc` files automatically when `legacy_version_file = true` (enabled by default).

Remove nvm from your shell profile and replace with mise activation:

```bash
# Remove from .zshrc:
# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Add to .zshrc:
eval "$(mise activate zsh)"
```

## From pyenv

Replace pyenv with mise for Python version management:

```bash
# pyenv (before)
# .python-version contains: 3.12.1
pyenv install 3.12.1
pyenv local 3.12.1

# mise (after)
mise use python@3.12.1
```

Mise reads `.python-version` files automatically.

Remove pyenv from your shell profile:

```bash
# Remove from .zshrc:
# export PYENV_ROOT="$HOME/.pyenv"
# eval "$(pyenv init -)"

# Add to .zshrc (if not already added):
eval "$(mise activate zsh)"
```

## From Makefiles

Replace Makefile targets with mise tasks:

```text
# Makefile (before)
.PHONY: build test lint fmt ci

build:
    cargo build --release

test:
    cargo test

lint:
    cargo clippy -- -D warnings

fmt:
    cargo fmt

ci: fmt lint test build
```

```toml
# mise.toml (after)
[tasks]
build = "cargo build --release"
test = "cargo test"
lint = "cargo clippy -- -D warnings"
fmt = "cargo fmt"

[tasks.ci]
depends = ["fmt", "lint", "test", "build"]
```

### Advantages Over Makefiles

| Feature         | Make                    | mise tasks                              |
| --------------- | ----------------------- | --------------------------------------- |
| Syntax          | Tab-sensitive, arcane   | TOML, readable                          |
| Dependencies    | File-based              | Task-based with `depends`               |
| Arguments       | Requires `$(ARGS)`      | Native `usage` spec or `--` passthrough |
| Watch mode      | External tool needed    | Built-in `mise watch`                   |
| Incremental     | File timestamps         | `sources`/`outputs` globs               |
| Cross-platform  | Requires make installed | Works on Linux, macOS, Windows          |
| Env management  | None                    | Built-in `[env]` section                |
| Tool management | None                    | Built-in `[tools]` section              |

## From direnv

Mise replaces direnv for per-directory environment variables:

```bash
# .envrc (before, direnv)
export NODE_ENV=development
export DATABASE_URL=postgres://localhost/mydb
dotenv .env.local

# mise.toml (after)
[env]
NODE_ENV = "development"
DATABASE_URL = "postgres://localhost/mydb"
_.file = ".env.local"
```

Remove direnv from your shell profile if fully migrating to mise.

## From Multiple Tools to One

A common migration consolidates several tools:

```bash
# Before: nvm + pyenv + direnv + Makefile
# .nvmrc, .python-version, .envrc, Makefile

# After: just mise.toml
```

```toml
# mise.toml replaces all four
[tools]
node = "22"
python = "3.12"

[env]
NODE_ENV = "development"
_.file = ".env.local"

[tasks]
build = "npm run build"
test = "pytest -v"
lint = "eslint src/ && ruff check ."

[tasks.ci]
depends = ["lint", "test", "build"]
```
