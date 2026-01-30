---
title: Actions
description: GitHub CLI workflow runs, manual triggers, run logs, rerun failed jobs, secrets, and variables management
tags: [gh-cli, actions, workflows, secrets, variables, ci-cd]
---

# Actions (CI/CD)

## Workflow Runs

```bash
gh run list
gh run view 12345
gh run watch 12345
gh run view 12345 --log
gh run rerun 12345 --failed
```

## Workflows

```bash
gh workflow list
gh workflow run deploy.yml
gh workflow run deploy.yml -f environment=production
gh workflow disable deploy.yml
gh workflow enable deploy.yml
```

## Secrets

```bash
gh secret list
gh secret set MY_SECRET
gh secret set MY_SECRET < secret.txt
gh secret delete MY_SECRET
```

## Variables

```bash
gh variable list
gh variable set MY_VAR --body "value"
```

## Check CI Status

```bash
gh pr checks
gh run watch
```
