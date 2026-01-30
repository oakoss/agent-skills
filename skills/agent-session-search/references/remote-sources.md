---
title: Remote Sources
description: Multi-machine search via SSH/rsync including setup wizard, manual configuration, path mappings, and source management
tags:
  [
    remote,
    sources,
    SSH,
    rsync,
    multi-machine,
    setup,
    wizard,
    path-mapping,
    sync,
    doctor,
  ]
---

# Remote Sources (Multi-Machine Search)

Search across sessions from multiple machines via SSH/rsync.

## Setup Wizard (Recommended)

```bash
cass sources setup
```

The wizard:

1. Discovers SSH hosts from `~/.ssh/config`
2. Probes each for agent data and cass installation
3. Optionally installs cass on remotes
4. Indexes sessions on remotes
5. Configures `sources.toml`
6. Syncs data locally

```bash
cass sources setup --hosts css,csd,yto  # Specific hosts only
cass sources setup --dry-run             # Preview without changes
cass sources setup --resume              # Resume interrupted setup
```

## Manual Setup

```bash
# Add a remote machine
cass sources add user@laptop.local --preset macos-defaults
cass sources add dev@workstation --path ~/.claude/projects --path ~/.codex/sessions

# List sources
cass sources list --json

# Sync sessions
cass sources sync
cass sources sync --source laptop --verbose

# Check connectivity
cass sources doctor
cass sources doctor --source laptop --json

# Path mappings (rewrite remote paths to local)
cass sources mappings list laptop
cass sources mappings add laptop --from /home/user/projects --to /Users/me/projects
cass sources mappings test laptop /home/user/projects/myapp/src/main.rs

# Remove source
cass sources remove laptop --purge -y
```

Configuration stored in `~/.config/cass/sources.toml` (Linux) or `~/Library/Application Support/cass/sources.toml` (macOS).
