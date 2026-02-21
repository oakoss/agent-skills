---
title: Advanced Git Operations
description: Commit signing, interactive rebase, worktrees, bisect, reflog recovery, and safe force-push patterns
tags:
  [
    signing,
    ssh,
    gpg,
    rebase,
    squash,
    worktree,
    bisect,
    reflog,
    force-with-lease,
  ]
---

# Advanced Git Operations

## Commit Signing

Signing commits proves authorship. SSH keys are preferred: simpler to set up, no extra tooling, and already used for push authentication.

### SSH Signing (Preferred)

```bash
# Configure git to use SSH for signing
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub

# Sign all commits automatically
git config --global commit.gpgsign true

# Verify a signed commit
git verify-commit HEAD
```

GitHub requires an allowed-signers file for SSH signature verification:

```bash
# Create allowed signers file
echo 'your@email.com namespaces="git" ssh-ed25519 AAAA...' > ~/.ssh/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
```

### GPG Signing (Legacy)

```bash
# List available GPG keys
gpg --list-secret-keys --keyid-format=long

# Configure git to use a specific key
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true

# Export public key to add to GitHub
gpg --armor --export <KEY_ID>
```

### Repository-Level Enforcement

```bash
# Require signed commits in a pre-receive hook (server-side)
# Or enforce via GitHub branch protection: "Require signed commits"
```

---

## Interactive Rebase

Rewrites commit history. Only use on commits that have NOT been pushed to a shared branch.

### Basic Usage

```bash
# Rebase last N commits interactively
git rebase -i HEAD~3

# Rebase all commits since branching from main
git rebase -i origin/main
```

### Commands in the Rebase Editor

| Command  | Effect                                          |
| -------- | ----------------------------------------------- |
| `pick`   | Keep commit as-is                               |
| `reword` | Keep commit, edit its message                   |
| `squash` | Meld into previous commit, combine messages     |
| `fixup`  | Meld into previous commit, discard this message |
| `drop`   | Remove commit entirely                          |
| `edit`   | Pause to amend the commit (files or message)    |

### Common Patterns

Squash work-in-progress commits before merging:

```bash
git rebase -i origin/main
# Change 'pick' to 'squash' on all commits after the first
```

Reorder commits (change the order of lines in the editor):

```bash
git rebase -i HEAD~4
# Move lines up or down to reorder commits
```

Split a commit:

```bash
git rebase -i HEAD~2
# Mark the target commit as 'edit'
# When paused:
git reset HEAD^           # unstage the commit
git add file-a.ts
git commit -m 'feat: add component'
git add file-b.ts
git commit -m 'test: add component tests'
git rebase --continue
```

### Abort and Recover

```bash
# Abort mid-rebase and return to original state
git rebase --abort

# If something went wrong after completing, restore with reflog
git reflog
git reset --hard HEAD@{<n>}
```

---

## Worktrees

Work on multiple branches simultaneously without stashing or switching. Each worktree is a separate working directory sharing the same repository.

### Basic Usage

```bash
# Add a worktree on an existing branch
git worktree add ../hotfix-123 fix/hotfix-123

# Add a worktree and create a new branch
git worktree add -b feat/new-feature ../feat-new-feature main

# List all worktrees
git worktree list

# Remove a worktree (after work is done)
git worktree remove ../hotfix-123
```

### Typical Workflow

```bash
# Start a long-running feature on main worktree
# Urgent fix arrives — add a second worktree without disturbing current work
git worktree add -b fix/critical-bug ../bug-fix origin/main

cd ../bug-fix
# Fix the bug, commit, push, open PR
git push -u origin fix/critical-bug

# Return to main worktree — original work is untouched
cd ../my-project

# Clean up after PR merges
git worktree remove ../bug-fix
git branch -d fix/critical-bug
```

### Constraints

- A branch can only be checked out in one worktree at a time
- `git stash` is per-worktree, not shared
- Worktrees share the same `.git` directory (hooks, config)

---

## Bisect

Binary-search through commit history to find which commit introduced a bug.

### Manual Bisect

```bash
# Start bisect session
git bisect start

# Mark current commit as bad (has the bug)
git bisect bad

# Mark a known-good commit (before the bug existed)
git bisect good v1.2.0

# Git checks out the midpoint — test it, then mark:
git bisect good   # this commit is fine
git bisect bad    # this commit has the bug

# Repeat until git reports the first bad commit
# Then end the session
git bisect reset
```

### Automated Bisect

Provide a script that exits `0` for good and non-zero for bad:

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.2.0

# Run automated bisect with a test script
git bisect run pnpm test -- --testPathPattern='auth.test.ts'

# Or with a custom script
git bisect run ./scripts/check-regression.sh

git bisect reset
```

### Bisect Log

```bash
# View the bisect decisions made so far
git bisect log

# Replay a saved bisect session
git bisect log > bisect.log
git bisect replay bisect.log
```

---

## Reflog

The reflog records every position HEAD and branch tips have been at, including rebases, resets, and amends. Objects remain recoverable until garbage collection runs (default: 90 days for reachable, 30 days for unreachable).

### Viewing the Reflog

```bash
# Show HEAD reflog
git reflog

# Show reflog for a specific branch
git reflog show feat/my-feature

# Show all reflogs
git reflog --all

# Show with timestamps
git reflog --format='%C(auto)%h %gd %gs (%cr)'
```

### Recovery Patterns

Recover commits lost after a hard reset:

```bash
git reflog
# Find the SHA before the reset (e.g. HEAD@{2})
git reset --hard HEAD@{2}
```

Recover a deleted branch:

```bash
git reflog
# Find the tip SHA of the deleted branch
git checkout -b recovered-branch <sha>
```

Recover a dropped stash:

```bash
git fsck --unreachable | grep commit
# Inspect candidates
git show <sha>
# Restore
git stash apply <sha>
```

---

## --force-with-lease vs --force

Never use `--force` on shared branches. It silently overwrites commits pushed by teammates.

```bash
# WRONG — overwrites any remote changes blindly
git push --force origin feat/my-feature

# CORRECT — fails if remote has commits not in your local ref
git push --force-with-lease origin feat/my-feature
```

`--force-with-lease` checks that the remote ref matches your last known state. If a teammate pushed since your last fetch, the push is rejected and you must integrate their changes first.

### When Force-Push Is Acceptable

- Your own feature branch (not yet reviewed or merged)
- After interactive rebase to clean up history before PR review
- Never on `main`, `master`, or any shared/protected branch

```bash
# Safe pattern: rebase then force-push with lease
git fetch origin
git rebase origin/main
git push --force-with-lease origin feat/my-feature
```
