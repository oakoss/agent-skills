---
title: Repos & Auth
description: GitHub CLI authentication, repository management, configuration, extensions, and aliases
tags: [gh-cli, auth, repos, config, extensions, aliases]
---

# Repos & Auth

## Authentication

```bash
gh auth status
gh auth login
gh auth refresh
```

## Repositories

```bash
gh repo clone owner/repo
gh repo create my-repo --public --source=. --push
gh repo fork owner/repo --clone
gh repo view --web
gh repo list
```

## Configuration

```bash
gh config list
gh config set editor vim
gh config set browser "open"
```

## Extensions

```bash
gh extension list
gh extension install owner/gh-extension
gh extension browse
```

## Aliases

```bash
gh alias set pv 'pr view'
gh alias list
```
