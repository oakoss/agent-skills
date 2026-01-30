---
title: Branching Strategies
description: Git Flow, GitHub Flow, GitLab Flow, One-Flow comparison and selection criteria for different team sizes and release models
tags: [branching, git-flow, github-flow, gitlab-flow, one-flow, release]
---

# Branching Strategies

## Git Flow

Best for regulated industries, physical hardware, or scheduled releases.

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Long-lived branches for new capabilities
- `release/*`: Preparation for a new production release
- `hotfix/*`: Urgent production fixes

```text
main ──────────────────────────────── production
  │                                      ▲
  └── develop ── feature/* ──────────────┘
       │                                 ▲
       └── release/* ────────────────────┘
       │                                 ▲
       └── hotfix/* ─────────────────────┘
```

## GitHub Flow

Best for high-growth SaaS and modern web apps.

- Everything happens on short-lived branches off `main`
- PRs are used for review and CI validation
- Once merged, the code is deployed immediately

```text
main ──────────────────────────────── always deployable
  │                  ▲
  └── feature-branch ┘ (short-lived, merged via PR)
```

## GitLab Flow (Environment-Based)

Best for projects with multiple deployment stages (staging, pre-prod, production).

- Use long-lived branches corresponding to environments
- Code flows through branches via merge requests

```text
main → staging → pre-production → production
```

## One-Flow (Simplified Git Flow)

Best for teams that need Git Flow's structure but find it too complex.

- Removes the `develop` branch
- Features and hotfixes all branch off and merge back into `main`

## Selection Criteria

| Strategy    | Speed      | Complexity | Reliability           | Best For                      |
| ----------- | ---------- | ---------- | --------------------- | ----------------------------- |
| Trunk-Based | Ultra High | Low        | High (requires tests) | Small-mid teams, SaaS, CI/CD  |
| GitHub Flow | High       | Low        | High                  | Web apps, startups            |
| Git Flow    | Low        | High       | Very High             | Regulated, scheduled releases |
| GitLab Flow | Medium     | Medium     | High                  | Multi-environment deployments |
| One-Flow    | Medium     | Medium     | High                  | Structured but simpler teams  |
| Stacked PRs | Ultra High | Moderate   | High                  | Large features, expert teams  |

### Decision Guide

1. **Default**: Trunk-based development with feature flags
2. **Multiple environments**: GitLab Flow
3. **Scheduled releases**: Git Flow or One-Flow
4. **Large features**: Stacked PRs on top of trunk-based
