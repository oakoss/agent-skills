---
title: Configuration
description: Environment variables, shell completions, API contract and versioning, installation, and integration with CASS Memory and Flywheel ecosystem
tags:
  [
    environment,
    variables,
    shell-completions,
    bash,
    zsh,
    fish,
    API,
    versioning,
    install,
    integration,
    CM,
    Flywheel,
  ]
---

# Configuration

## Environment Variables

| Variable                               | Purpose                               |
| -------------------------------------- | ------------------------------------- |
| `CASS_DATA_DIR`                        | Override data directory               |
| `CHATGPT_ENCRYPTION_KEY`               | Base64 key for encrypted ChatGPT      |
| `PI_CODING_AGENT_DIR`                  | Override Pi-Agent sessions path       |
| `CASS_CACHE_SHARD_CAP`                 | Per-shard cache entries (default 256) |
| `CASS_CACHE_TOTAL_CAP`                 | Total cached hits (default 2048)      |
| `CASS_DEBUG_CACHE_METRICS`             | Enable cache debug logging            |
| `CODING_AGENT_SEARCH_NO_UPDATE_PROMPT` | Skip update checks                    |

## Shell Completions

```bash
cass completions bash > ~/.local/share/bash-completion/completions/cass
cass completions zsh > "${fpath[1]}/_cass"
cass completions fish > ~/.config/fish/completions/cass.fish
cass completions powershell >> $PROFILE
```

## API Contract and Versioning

```bash
cass api-version --json
# → { "version": "0.4.0", "contract_version": "1", "breaking_changes": [] }

cass introspect --json
# → Full schema: all commands, arguments, response types
```

**Guaranteed Stable:**

- Exit codes and their meanings
- JSON response structure for `--robot` output
- Flag names and behaviors
- `_meta` block format

## Installation

```bash
# One-liner install (Linux/macOS)
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/coding_agent_session_search/main/install.sh \
  | bash -s -- --easy-mode --verify

# Windows
irm https://raw.githubusercontent.com/Dicklesworthstone/coding_agent_session_search/main/install.ps1 | iex
```

## Integration with CASS Memory (cm)

CASS provides **episodic memory** (raw sessions). CM extracts **procedural memory** (rules and playbooks):

```bash
# 1. CASS indexes raw sessions
cass index --full

# 2. Search for relevant past experience
cass search "authentication timeout" --robot --limit 10

# 3. CM reflects on sessions to extract rules
cm reflect
```

## Integration with Flywheel

| Tool           | Integration                                                  |
| -------------- | ------------------------------------------------------------ |
| **CM**         | CASS provides episodic memory, CM extracts procedural memory |
| **NTM**        | Robot mode flags for searching past sessions                 |
| **Agent Mail** | Search threads across agent history                          |
| **BV**         | Cross-reference beads with past solutions                    |
