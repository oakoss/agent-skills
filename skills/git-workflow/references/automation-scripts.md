---
title: Automation Scripts
description: Branch pruning, semantic release, security scanning, stacked PR helpers, and repository maintenance scripts
tags: [automation, pruning, semantic-release, gitleaks, maintenance]
---

# Automation Scripts

## Branch Pruning

Remove merged branches and clean up local caches:

```bash
# Prune remote tracking branches
git fetch --prune

# Delete local branches that have been merged to main
git branch --merged main | grep -v "main" | xargs -n 1 git branch -d

# Delete branches merged to current branch
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d
```

## Stale Branch Cleanup

Find and clean branches older than a threshold:

```bash
# List branches sorted by last commit date
git for-each-ref --sort=-committerdate refs/heads/ --format='%(committerdate:short) %(refname:short)'

# Find branches with no activity in 30+ days
git for-each-ref --sort=-committerdate refs/heads/ --format='%(committerdate:relative) %(refname:short)' | grep -E "(month|year)"
```

## Semantic Release

Automate versioning and changelog generation based on conventional commits:

```bash
# Run semantic release (reads commit history, bumps version, publishes)
pnpm dlx semantic-release

# Dry run to preview next version
pnpm dlx semantic-release --dry-run
```

Alternative with Changesets:

```bash
# Initialize changesets
pnpm dlx @changesets/cli init

# Add a changeset
pnpm changeset

# Version packages based on changesets
pnpm changeset version

# Publish
pnpm changeset publish
```

## Security Scanning

Scan for secrets before pushing:

```bash
# Scan current directory for leaked secrets
pnpm dlx gitleaks detect --source . --verbose

# Scan git history for secrets
pnpm dlx gitleaks detect --source . --verbose --log-opts="--all"
```

## Stacked PR Helpers

```bash
# Graphite: Restack all dependent branches
gt restack

# Manual: Rebase a branch onto a new base
git rebase --onto new-base old-base branch-to-move
```

## Repository Maintenance

```bash
# Full repository cleanup
git gc --aggressive --prune=now

# Verify repository integrity
git fsck --full

# Show repository size statistics
git count-objects -v -H
```
