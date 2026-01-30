---
title: Safety Patterns and Edge Cases
description: Detailed breakdown of blocked commands, safe alternatives, and edge cases DCG handles
tags: [safety, patterns, edge-cases, git, filesystem]
---

# Safety Patterns and Edge Cases

## What DCG Blocks

### Git Commands That Destroy Uncommitted Work

| Command                                   | Reason                              |
| ----------------------------------------- | ----------------------------------- |
| `git reset --hard`                        | Destroys uncommitted changes        |
| `git reset --merge`                       | Destroys uncommitted changes        |
| `git checkout -- <file>`                  | Discards file modifications         |
| `git restore <file>` (without `--staged`) | Discards uncommitted changes        |
| `git clean -f`                            | Permanently deletes untracked files |

### Git Commands That Destroy Remote History

| Command                   | Reason                            |
| ------------------------- | --------------------------------- |
| `git push --force` / `-f` | Overwrites remote commits         |
| `git branch -D`           | Force-deletes without merge check |

### Git Commands That Destroy Stashed Work

| Command           | Reason                          |
| ----------------- | ------------------------------- |
| `git stash drop`  | Permanently deletes a stash     |
| `git stash clear` | Permanently deletes all stashes |

### Filesystem Commands

| Command                                          | Reason                          |
| ------------------------------------------------ | ------------------------------- |
| `rm -rf` (outside `/tmp`, `/var/tmp`, `$TMPDIR`) | Recursive deletion is dangerous |

## What DCG Allows

### Always Safe Git Operations

`git status`, `git log`, `git diff`, `git add`, `git commit`, `git push`, `git pull`, `git fetch`, `git branch -d` (safe delete with merge check), `git stash`, `git stash pop`, `git stash list`

### Explicitly Safe Patterns

| Pattern                          | Why Safe                                    |
| -------------------------------- | ------------------------------------------- |
| `git checkout -b <branch>`       | Creating new branches                       |
| `git checkout --orphan <branch>` | Creating orphan branches                    |
| `git restore --staged <file>`    | Unstaging only, does not touch working tree |
| `git restore -S <file>`          | Short flag for staged                       |
| `git clean -n` / `--dry-run`     | Preview mode, no actual deletion            |
| `rm -rf /tmp/*`                  | Temp directories are ephemeral              |
| `rm -rf $TMPDIR/*`               | Shell variable forms                        |

### Safe Alternative: `--force-with-lease`

```bash
git push --force-with-lease   # ALLOWED - refuses if remote has unseen commits
git push --force              # BLOCKED - can overwrite others' work
```

## Edge Cases Handled

### Path Normalization

```bash
/usr/bin/git reset --hard          # Blocked
/usr/local/bin/git checkout -- .   # Blocked
/bin/rm -rf /home/user             # Blocked
```

### Flag Ordering Variants

```bash
rm -rf /path          # Combined flags
rm -fr /path          # Reversed order
rm -r -f /path        # Separate flags
rm --recursive --force /path    # Long flags
```

All variants are handled.

### Shell Variable Expansion

```bash
rm -rf $TMPDIR/build           # Allowed (temp)
rm -rf ${TMPDIR}/build         # Allowed
rm -rf "$TMPDIR/build"         # Allowed
rm -rf "${TMPDIR:-/tmp}/build" # Allowed
```

### Staged vs Worktree Restore

```bash
git restore --staged file.txt    # Allowed (unstaging only)
git restore -S file.txt          # Allowed (short flag)
git restore file.txt             # BLOCKED (discards changes)
git restore --worktree file.txt  # BLOCKED (explicit worktree)
git restore -S -W file.txt       # BLOCKED (includes worktree)
```

## Security Considerations

### What DCG Protects Against

- Accidental data loss from `git checkout --` or `git reset --hard`
- Remote history destruction from force pushes
- Stash loss from `git stash drop/clear`
- Filesystem accidents from `rm -rf` outside temp directories

### What DCG Does NOT Protect Against

- Malicious actors (can bypass the hook)
- Non-Bash commands (Python/JavaScript file writes, API calls)
- Committed but unpushed work
- Commands inside scripts (`./deploy.sh` contents not inspected)

### Threat Model

DCG assumes the AI agent is **well-intentioned but fallible**. It catches honest mistakes, not adversarial attacks.
