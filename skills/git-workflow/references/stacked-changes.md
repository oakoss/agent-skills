---
title: Stacked Changes
description: Stacked PRs concept, manual stacking with git CLI, Graphite automation, and best practices for large feature development
tags: [stacked-prs, graphite, rebase, code-review, incremental]
---

# Stacked Changes

Break large features into a series of small, dependent pull requests. Reviewers only see 100-200 lines at a time, making reviews faster and more thorough.

## The Concept

Instead of one giant PR:

```text
Feature A (1,000 lines) -> One giant PR (slow review, high risk)
```

Use stacked PRs:

```text
Part 1: Database Schema (100 lines) -> PR #1
Part 2: API Client (150 lines)      -> PR #2 (depends on #1)
Part 3: UI Component (200 lines)    -> PR #3 (depends on #2)
```

## Manual Stacking with Git CLI

```bash
# Create the first part
git checkout main
git checkout -b part-1
# ... make changes, commit, push ...
git push -u origin part-1

# Create the second part on top of part-1
git checkout -b part-2  # branches from part-1
# ... make changes, commit, push ...
git push -u origin part-2

# When part-1 changes, rebase part-2
git checkout part-2
git rebase part-1

# For deeper stacks, use --onto
git rebase --onto new-base old-base branch-to-rebase
```

## Automated Stacking with Graphite

Graphite automates the rebase/restack process:

```bash
# Create a new branch with a commit in the stack
gt create -am "feat: add database schema"

# Insert a branch mid-stack (rebases subsequent branches automatically)
gt create --insert -am "fix: add missing migration"

# Push all branches in the stack as separate PRs
gt submit --stack

# Modify the current branch and restack descendants
gt modify

# Automatically rebase all dependent branches when a parent changes
gt restack

# Pull trunk changes and restack; clean up merged branches
gt sync
```

## Benefits

- **Parallel Review**: Different experts can review different parts simultaneously
- **Atomic Reverts**: Revert PR #3 without losing the DB schema in PR #1
- **Reduced Cognitive Load**: Reviewers focus on 100-200 lines at a time
- **Faster Merge Cycles**: Small PRs get approved faster

## Best Practices

1. **Title your stacks**: `[1/3] Database Setup`, `[2/3] API Implementation`, `[3/3] UI Component`
2. **Merge in order**: Always merge the base of the stack first
3. **Restack frequently**: Keep your stack healthy by restacking against `main` daily
4. **Aim for ~100-200 lines per PR**: Right size for thorough review
5. **Independent when possible**: Design stack slices to minimize cross-PR dependencies
