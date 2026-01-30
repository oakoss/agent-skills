---
title: Configuration
description: RU XDG-compliant directory structure, repo list format, layout modes, per-repo agent configuration, and update strategies
tags: [configuration, xdg, repo-list, layout, per-repo-config]
---

# Configuration

## XDG-Compliant Directory Structure

```sh
~/.config/ru/
├── config               # Main config file
└── repos.d/
    ├── public.list      # Public repos (one per line)
    └── private.list     # Private repos (gitignored)

~/.local/state/ru/
├── logs/
│   └── YYYY-MM-DD/
├── agent-sweep/
│   ├── state.json
│   └── results.ndjson
└── review/
    ├── digests/
    └── results/
```

## Repo List Format

```sh
# ~/.config/ru/repos.d/public.list
owner/repo
another-owner/another-repo@develop
private-org/repo@main as local-name
https://github.com/owner/repo.git
```

## Layout Modes

| Layout       | Example Path                           |
| ------------ | -------------------------------------- |
| `flat`       | `/data/projects/repo`                  |
| `owner-repo` | `/data/projects/owner_repo`            |
| `full`       | `/data/projects/github.com/owner/repo` |

```bash
ru config --set LAYOUT=owner-repo
```

## Per-Repo Configuration

```yaml
# ~/.../your-repo/.ru-agent.yml
agent_sweep:
  enabled: true
  max_file_size: 5242880 # 5MB
  extra_context: 'This is a Python project using FastAPI'
  pre_hook: 'make lint'
  post_hook: 'make test'
  denylist_extra:
    - '*.backup'
    - 'internal/*'
```

## Update Strategies

```bash
ru sync                        # Default: ff-only (safest)
ru sync --rebase               # Rebase local commits
ru sync --autostash            # Auto-stash before pull
ru sync --force                # Force update (use with caution)
```

## Quality Gates

Auto-detection by project type:

| Project Type  | Test Command    | Lint Command        |
| ------------- | --------------- | ------------------- |
| npm/yarn      | `npm test`      | `npm run lint`      |
| Cargo (Rust)  | `cargo test`    | `cargo clippy`      |
| Go            | `go test ./...` | `golangci-lint run` |
| Python        | `pytest`        | `ruff check`        |
| Makefile      | `make test`     | `make lint`         |
| Shell scripts | (none)          | `shellcheck *.sh`   |

## Rate Limiting

Adaptive parallelism governor:

| Condition              | Action                     |
| ---------------------- | -------------------------- |
| GitHub remaining < 100 | Reduce parallelism to 1    |
| GitHub remaining < 500 | Reduce parallelism by 50%  |
| Model 429 detected     | Pause new sessions for 60s |
| Error rate > 50%       | Open circuit breaker       |
