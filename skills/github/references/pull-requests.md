---
title: Pull Requests
description: GitHub CLI pull request creation, review workflows, merge strategies, checkout, checks, and diff viewing
tags: [gh-cli, pull-requests, review, merge, checks]
---

# Pull Requests

## List and View

```bash
gh pr list
gh pr view 45
gh pr view 45 --web
gh pr diff 45
gh pr checks 45
```

## Create

```bash
gh pr create --title "Add feature" --body "Description"
gh pr create --fill  # from current branch, auto-fill title/body
```

## Checkout

```bash
gh pr checkout 45
```

## Review

```bash
gh pr review 45 --approve
gh pr review 45 --request-changes --body "Please fix X"
gh pr review 45 --comment --body "Looks good but..."
```

## Merge

```bash
gh pr merge 45 --squash
gh pr merge 45 --merge
gh pr merge 45 --rebase
gh pr merge --squash --delete-branch  # current PR
```

## Close

```bash
gh pr close 45
```

## Quick PR Workflow

```bash
git checkout -b feature/my-feature
# ... make changes ...
git add . && git commit -m "Add feature"
git push -u origin feature/my-feature
gh pr create --fill
```

## Review and Merge Workflow

```bash
gh pr checkout 45
# ... review code ...
gh pr review --approve
gh pr merge --squash --delete-branch
```
