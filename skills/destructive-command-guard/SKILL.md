---
name: destructive-command-guard
description: 'Blocks dangerous commands before execution via a Rust-based Claude Code hook. Use when configuring agent safety guards, setting up destructive command blocking, or auditing CLI protection rules. Use for git reset protection, rm -rf interception, force-push blocking, and pack-based command filtering.'
---

# Destructive Command Guard

A high-performance Claude Code hook that intercepts and blocks destructive commands before they execute. Written in Rust with SIMD-accelerated filtering for sub-millisecond latency. Assumes agents are well-intentioned but fallible.

## Overview

DCG uses a whitelist-first architecture: safe patterns are checked before destructive patterns, and unrecognized commands are allowed by default. This ensures legitimate workflows are never broken while known dangerous patterns are always blocked.

## Quick Reference

| Category         | Blocked Commands                                                                   |
| ---------------- | ---------------------------------------------------------------------------------- |
| Uncommitted work | `git reset --hard`, `git checkout -- <file>`, `git restore <file>`, `git clean -f` |
| Remote history   | `git push --force` / `-f`, `git branch -D`                                         |
| Stashed work     | `git stash drop`, `git stash clear`                                                |
| Filesystem       | `rm -rf` (outside `/tmp`, `/var/tmp`, `$TMPDIR`)                                   |

| Category      | Allowed Commands                                                                                                                                 |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Safe git      | `git status`, `git log`, `git diff`, `git add`, `git commit`, `git push`, `git pull`, `git fetch`, `git branch -d`, `git stash`, `git stash pop` |
| Safe patterns | `git checkout -b`, `git restore --staged`, `git clean -n`, `git push --force-with-lease`                                                         |
| Temp dirs     | `rm -rf /tmp/*`, `rm -rf $TMPDIR/*`                                                                                                              |

| Setting              | Value                                |
| -------------------- | ------------------------------------ |
| Exit code (safe)     | `0`                                  |
| Exit code (blocked)  | `2`                                  |
| Default behavior     | Allow (fail-safe)                    |
| Pattern priority     | Safe checked first, then destructive |
| Safe patterns        | 34                                   |
| Destructive patterns | 16                                   |

## Common Mistakes

| Mistake                                                          | Correct Pattern                                                               |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Forgetting to restart Claude Code after adding the hook          | Always restart Claude Code after modifying `~/.claude/settings.json`          |
| Using `DCG_BYPASS=1` permanently in shell profile                | Only set bypass temporarily for a single command, then remove it              |
| Assuming DCG inspects commands inside scripts                    | DCG only inspects direct Bash tool invocations, not contents of `./deploy.sh` |
| Blocking `git branch -d` (lowercase) thinking it is destructive  | Lowercase `-d` is safe (merge-checked); only uppercase `-D` force-deletes     |
| Not enabling database or cloud packs for production environments | Configure relevant packs in `~/.config/dcg/config.toml` for your stack        |

## Delegation

- **Audit which destructive commands an agent session has attempted**: Use `Explore` agent
- **Set up DCG with custom packs for a new project environment**: Use `Task` agent
- **Plan a layered safety architecture combining DCG with other guardrails**: Use `Plan` agent

## References

- [Command detection and processing pipeline](references/command-detection.md)
- [Pack configuration and environment variables](references/pack-configuration.md)
- [Installation and Claude Code setup](references/installation.md)
- [Safety patterns and edge cases](references/safety-patterns.md)
- [Troubleshooting and FAQ](references/troubleshooting.md)
