---
title: Trunk-Based Development
description: Core principles, workflow steps, feature flags for incomplete work, and anti-patterns for high-velocity teams
tags: [trunk-based, feature-flags, continuous-integration, short-lived-branches]
---

# Trunk-Based Development

The preferred workflow for high-velocity teams. Focuses on small, frequent merges to a single `main` branch to minimize integration hell.

## Core Principles

- **Short-Lived Branches**: Branches should exist for hours, not days (max 48 hours)
- **Continuous Integration**: Code is merged to `main` at least once a day
- **Feature Flags**: Incomplete features are merged behind flags to keep `main` always deployable
- **Automated Testing**: All merges must pass CI; broken main is an emergency

## Workflow

```bash
# 1. Start from latest main
git checkout main
git pull --rebase origin main

# 2. Create a tiny branch
git checkout -b fix/auth-header

# 3. Implement and test
# ... edit files ...
pnpm test
pnpm typecheck

# 4. Push and create PR
git push -u origin fix/auth-header
gh pr create --title "fix(auth): correct header validation"

# 5. Merge immediately after approval
gh pr merge --squash
```

## Feature Flags for Incomplete Work

Instead of long-lived feature branches, merge behind flags:

```ts
if (flags.isEnabled('new-checkout-flow')) {
  return <NewCheckout />
}
return <LegacyCheckout />
```

This allows merging incomplete code into `main` safely while it is still in progress.

## When to Use

- **Small to mid-sized teams**: Fast communication and high trust
- **Microservices**: Isolated domains where breaking changes have limited blast radius
- **SaaS products**: Environments requiring multiple deployments per day

## When NOT to Use

- Regulated industries requiring formal release processes (use Git Flow)
- Teams without adequate test coverage (fix tests first)
- Projects with long QA cycles before deployment

## Anti-Patterns

| Anti-Pattern                | Problem                               | Fix                                  |
| --------------------------- | ------------------------------------- | ------------------------------------ |
| Merging broken code         | Red main is an emergency              | Require 100% test pass rate on main  |
| Large PRs                   | Defeats rapid integration purpose     | Keep PRs under 200 lines             |
| Ignoring the build          | Cascading failures for the whole team | Fix red main immediately             |
| Branches living over 48 hrs | Integration hell, stale code          | Break work into smaller increments   |
| No feature flags            | Cannot merge incomplete work          | Use flags to decouple deploy/release |
