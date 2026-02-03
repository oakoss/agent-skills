---
title: Actions
description: GitHub CLI workflow runs, manual triggers, run logs, rerun failed jobs, secrets, variables, cache management, and artifact downloads
tags:
  [
    gh-cli,
    actions,
    workflows,
    secrets,
    variables,
    ci-cd,
    cache,
    artifacts,
    runs,
  ]
---

# Actions (CI/CD)

## Workflow Runs

### List Runs

```bash
gh run list
gh run list --workflow deploy.yml
gh run list --branch main --limit 10
gh run list --status failure
gh run list --user @me
gh run list --event push
gh run list --commit abc1234
gh run list --json databaseId,status,conclusion,headBranch
```

### View Run Details

```bash
gh run view 12345
gh run view 12345 --web
gh run view 12345 --json jobs
gh run view 12345 --verbose
gh run view 12345 --log
gh run view 12345 --log-failed
gh run view 12345 --job 67890
gh run view 12345 --attempt 2
gh run view 12345 --exit-status
```

### Watch a Run

```bash
gh run watch 12345
gh run watch 12345 --exit-status
gh run watch 12345 --interval 5
gh run watch 12345 --compact
```

### Rerun

```bash
gh run rerun 12345
gh run rerun 12345 --failed
gh run rerun 12345 --job 67890
gh run rerun 12345 --debug
```

### Cancel and Delete

```bash
gh run cancel 12345
gh run cancel 12345 --force
gh run delete 12345
```

### Download Artifacts

```bash
gh run download 12345
gh run download 12345 --name "build-output"
gh run download 12345 --pattern "*.zip"
gh run download 12345 --dir ./artifacts
```

## Workflows

### List and View

```bash
gh workflow list
gh workflow list --all
gh workflow view deploy.yml
gh workflow view deploy.yml --web
```

### Trigger a Workflow

```bash
gh workflow run deploy.yml
gh workflow run deploy.yml -f environment=production
gh workflow run deploy.yml -f environment=staging -f version=1.2.3
gh workflow run deploy.yml --ref feature-branch
```

### Enable and Disable

```bash
gh workflow disable deploy.yml
gh workflow enable deploy.yml
```

## Secrets

```bash
gh secret list
gh secret list --json name,updatedAt
gh secret set MY_SECRET
gh secret set MY_SECRET --body "secret-value"
gh secret set MY_SECRET < secret.txt
gh secret set MY_SECRET --env production
gh secret set MY_SECRET --org my-org --visibility all
gh secret delete MY_SECRET
gh secret delete MY_SECRET --env production
```

Key flags for `gh secret set`:

- `--env` -- set an environment-level secret
- `--org` -- set an organization-level secret
- `--visibility` -- organization secret visibility: `all`, `private`, `selected`
- `--repos` -- list of repositories for selected visibility

## Variables

```bash
gh variable list
gh variable list --json name,value
gh variable get MY_VAR
gh variable set MY_VAR --body "value"
gh variable set MY_VAR --env production --body "prod-value"
gh variable set MY_VAR --org my-org --visibility all --body "org-value"
gh variable delete MY_VAR
```

## Cache Management

```bash
gh cache list
gh cache list --json id,key,sizeInBytes
gh cache list --limit 50
gh cache delete cache-key-or-id
gh cache delete --all
```

## Check CI Status

For the current PR:

```bash
gh pr checks
gh pr checks --watch
gh pr checks --json name,state,conclusion
gh run watch
```
