---
title: Configuration
description: Mise configuration files, settings, activation, and project setup
tags: [config, settings, activate, mise.toml, global, local, trust, doctor]
---

# Configuration

## Configuration File Locations

Mise reads configuration from multiple locations, merged in priority order:

| File                           | Scope   | Purpose                              |
| ------------------------------ | ------- | ------------------------------------ |
| `mise.toml`                    | Project | Committed, shared with team          |
| `.mise.local.toml`             | Project | Gitignored, personal overrides       |
| `.mise.<env>.toml`             | Project | Environment-specific (staging, prod) |
| `~/.config/mise/config.toml`   | Global  | Default tools and settings           |
| `~/.config/mise/settings.toml` | Global  | Mise behavior settings               |

## Complete mise.toml Example

```toml
min_version = "2024.11.1"

[tools]
node = "22"
python = "3.12"
"npm:prettier" = "latest"

[env]
NODE_ENV = "development"
_.file = [".env", ".env.local"]
_.path = ["./node_modules/.bin"]

[tasks]
dev = "npm run dev"
build = "npm run build"
test = "npm test"
lint = "npm run lint"

[tasks.ci]
depends = ["lint", "test", "build"]
```

## Shell Activation

Add mise activation to your shell profile for automatic tool switching on `cd`:

```bash
# ~/.bashrc or ~/.bash_profile
eval "$(mise activate bash)"

# ~/.zshrc
eval "$(mise activate zsh)"

# ~/.config/fish/config.fish
mise activate fish | source
```

Without activation, use `mise exec` to run commands with mise-managed tools:

```bash
mise exec -- node --version
mise exec -- python script.py
```

## Settings

Configure mise behavior in `~/.config/mise/settings.toml`:

```toml
[settings]
# Automatically install missing tools on cd
auto_install = true

# Use verbose output
verbose = false

# Number of parallel jobs for installations
jobs = 4

# Experimental features
experimental = false

# Legacy version file support (.nvmrc, .python-version, etc.)
legacy_version_file = true

# Always keep this many versions installed
always_keep_download = false
```

### Legacy Version File Support

Mise can read existing version files from other managers:

| File                       | Tool Manager  |
| -------------------------- | ------------- |
| `.nvmrc` / `.node-version` | nvm / fnm     |
| `.python-version`          | pyenv         |
| `.ruby-version`            | rbenv         |
| `.java-version`            | jenv / sdkman |
| `.tool-versions`           | asdf          |

Enable with:

```toml
[settings]
legacy_version_file = true
```

## Diagnostics

```bash
# Check mise installation and configuration
mise doctor

# Show resolved configuration
mise settings

# Show which config files are active
mise config ls

# Show tool installation paths
mise where node
```

## Minimum Version Pinning

Enforce a minimum mise version for your project:

```toml
min_version = "2024.11.1"
```

Team members with older versions get a clear error message to upgrade.

## Project Initialization

```bash
# Create a new mise.toml with common defaults
mise init

# Or manually create mise.toml and add tools
mise use node@22
mise use python@3.12
```

## Git Integration

Recommended `.gitignore` entries:

```text
.mise.local.toml
.env.local
.env.*.local
```

Committed files:

```text
mise.toml
.env
```

## IDE Integration

Mise provides shims for IDE compatibility:

```bash
# Enable shims (for IDEs that don't support mise activate)
mise settings set shims_on_path true

# Reshim after installing new tools
mise reshim
```

Shims are located at `~/.local/share/mise/shims/`. Add this to your IDE's PATH for tool discovery.
