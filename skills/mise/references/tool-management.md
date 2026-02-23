---
title: Tool Management
description: Installing, pinning, and managing development tool versions across languages using mise backends
tags:
  [install, use, pin, backends, npm, cargo, pipx, github, asdf, versions, tools]
---

# Tool Management

## Installing and Pinning Tools

The `mise use` command installs a tool and writes it to `mise.toml`:

```bash
mise use node@22
mise use python@3.12
mise use go@1.22
mise use terraform@1.7
```

Pin an exact version (disables fuzzy matching):

```bash
mise use --pin node@22.11.0
```

Pin globally (applies to all projects without local config):

```bash
mise use -g node@22
```

Install all tools from existing `mise.toml` without modifying the file:

```bash
mise install
```

## Tool Version Syntax

```toml
[tools]
# Fuzzy version - resolves to latest 22.x.x
node = "22"

# Exact version
python = "3.12.1"

# Latest available
go = "latest"

# LTS (for tools that support it)
node = "lts"

# Multiple versions (first is default)
python = ["3.12", "3.11"]

# Prefix match
ruby = "3.3"
```

## Backends

Mise supports multiple backends for installing tools beyond the default asdf plugin registry:

```toml
[tools]
# Core tools (built-in, no plugin needed)
node = "22"
python = "3.12"
go = "1.22"
java = "21"
ruby = "3.3"
rust = "1.77"

# npm packages
"npm:prettier" = "latest"
"npm:eslint" = "9"
"npm:tsx" = "4"

# Python packages via pipx
"pipx:black" = "24"
"pipx:ruff" = "latest"

# Cargo crates
"cargo:cargo-watch" = "latest"
"cargo:ripgrep" = "14"

# GitHub releases
"github:BurntSushi/ripgrep" = "latest"
"github:sharkdp/fd" = "10"

# Go packages
"go:mvdan.cc/gofumpt" = "latest"

# Ubi (universal binary installer)
"ubi:cli/cli" = "latest"
```

## Tool Options

Tools can include additional configuration:

```toml
[tools]
# Postinstall hook
node = { version = "22", postinstall = "corepack enable" }

# OS-specific tools
ripgrep = { version = "latest", os = ["linux", "macos"] }

# Architecture-specific
sometool = { version = "1.0", arch = ["x86_64"] }
```

## Listing and Managing Versions

```bash
# List all installed tools and their versions
mise ls

# List installed versions of a specific tool
mise ls node

# Show outdated tools
mise outdated

# Upgrade tools to latest within constraints
mise upgrade

# Upgrade a specific tool
mise upgrade node

# Remove a tool version
mise uninstall node@20

# Prune unused tool versions
mise prune

# Show where a tool is installed
mise where node@22

# Show the active version of a tool
mise current node
```

## Version Resolution Order

Mise resolves tool versions in this priority order:

1. `MISE_<TOOL>_VERSION` environment variable
2. `mise.toml` in current directory
3. `mise.toml` in parent directories (walks up)
4. `.tool-versions` file (asdf compatibility)
5. `~/.config/mise/config.toml` (global default)

## Config File Formats

```toml
# mise.toml (preferred)
[tools]
node = "22"
python = "3.12"
```

Legacy format (`.tool-versions`, asdf-compatible):

```text
node 22
python 3.12
```

Mise reads both formats. The `mise.toml` format supports all features (tasks, env, backends). The `.tool-versions` format only supports tool versions.

## Trust and Security

Mise requires explicit trust for config files from untrusted sources:

```bash
# Trust the config in current directory
mise trust

# Trust a specific file
mise trust mise.toml

# Revoke trust
mise trust --untrust
```

Untrusted configs are ignored until trusted. This prevents malicious `mise.toml` files from executing arbitrary code when you clone a repository.
