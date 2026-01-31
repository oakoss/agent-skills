---
title: Configuration
description: Environment variables, shell completions, installation methods, and integration with CASS Memory and Flywheel ecosystem
tags:
  [
    environment,
    variables,
    shell-completions,
    bash,
    zsh,
    fish,
    install,
    integration,
    CM,
    Flywheel,
    Homebrew,
    Scoop,
  ]
---

# Configuration

## Environment Variables

| Variable                               | Purpose                                   |
| -------------------------------------- | ----------------------------------------- |
| `CASS_DATA_DIR`                        | Override data directory                   |
| `CHATGPT_ENCRYPTION_KEY`               | Base64 key for encrypted ChatGPT sessions |
| `PI_CODING_AGENT_DIR`                  | Override Pi-Agent sessions path           |
| `CODING_AGENT_SEARCH_NO_UPDATE_PROMPT` | Skip update checks                        |

## Shell Completions

```bash
cass completions bash > ~/.local/share/bash-completion/completions/cass
cass completions zsh > "${fpath[1]}/_cass"
cass completions fish > ~/.config/fish/completions/cass.fish
cass completions powershell >> $PROFILE
```

## Installation

```bash
# One-liner install (Linux/macOS)
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/coding_agent_session_search/main/install.sh \
  | bash -s -- --easy-mode --verify

# Windows (Scoop)
scoop bucket add dicklesworthstone https://github.com/Dicklesworthstone/scoop-bucket
scoop install dicklesworthstone/cass

# macOS/Linux (Homebrew)
brew install dicklesworthstone/tap/cass
```

Remote install fallback chain (for multi-machine setup):

1. cargo-binstall (~30s)
2. Pre-built binary (~10s)
3. cargo install (~5min)
4. Full bootstrap with rustup (~10min)

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

| Tool    | Integration                                                  |
| ------- | ------------------------------------------------------------ |
| **CM**  | CASS provides episodic memory, CM extracts procedural memory |
| **NTM** | Robot mode flags for searching past sessions                 |
| **BV**  | Cross-reference beads with past solutions                    |
