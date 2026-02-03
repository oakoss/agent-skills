---
title: Repos & Auth
description: GitHub CLI authentication, repository management, configuration, extensions, and aliases
tags: [gh-cli, auth, repos, config, extensions, aliases, sync, fork, clone]
---

# Repos & Auth

## Authentication

```bash
gh auth login
gh auth login --with-token < token.txt
gh auth status
gh auth status --json
gh auth token
gh auth refresh -s read:org,admin:public_key
gh auth switch
gh auth logout
gh auth setup-git
```

Key flags for `gh auth login`:

- `--hostname` -- authenticate with a specific GitHub host (GitHub Enterprise)
- `--web` -- open a browser for authentication
- `--with-token` -- read token from stdin
- `--scopes` -- request additional OAuth scopes

Check current authentication and scopes:

```bash
gh auth status
```

## Repositories

### Clone and Fork

```bash
gh repo clone owner/repo
gh repo clone owner/repo -- --depth 1
gh repo fork owner/repo --clone
gh repo fork owner/repo --clone --remote
```

### Create

```bash
gh repo create my-repo --public
gh repo create my-repo --private --clone
gh repo create my-repo --public --source=. --push
gh repo create org/my-repo --internal --template owner/template-repo
```

### View and List

```bash
gh repo view
gh repo view owner/repo --web
gh repo view --json name,description,url
gh repo list owner --limit 50
gh repo list owner --json name,isPrivate --jq '.[].name'
```

### Edit and Manage

```bash
gh repo edit --description "New description"
gh repo edit --default-branch main
gh repo edit --enable-issues --enable-wiki=false
gh repo archive owner/repo
gh repo unarchive owner/repo
gh repo rename new-name
gh repo delete owner/repo --yes
```

### Sync

Sync a fork with its upstream:

```bash
gh repo sync owner/my-fork
gh repo sync --source owner/upstream
gh repo set-default owner/repo
```

### Deploy Keys

```bash
gh repo deploy-key list
gh repo deploy-key add key.pub --title "CI server"
gh repo deploy-key delete 12345
```

### Autolinks

```bash
gh repo autolink list
gh repo autolink create "TICKET-" "https://jira.example.com/browse/TICKET-<num>"
gh repo autolink view 1
gh repo autolink delete 1
```

### Gitignore and License Templates

```bash
gh repo gitignore list
gh repo gitignore view Node
gh repo license list
gh repo license view mit
```

## Configuration

```bash
gh config list
gh config set editor vim
gh config set browser "open"
gh config set git_protocol ssh
gh config get editor
gh config clear-cache
```

## Browse

Open the current repository in the browser:

```bash
gh browse
gh browse --settings
gh browse --projects
gh browse src/main.ts
gh browse src/main.ts:42
```

## Extensions

```bash
gh extension list
gh extension install owner/gh-extension-name
gh extension search query
gh extension browse
gh extension upgrade --all
gh extension remove extension-name
gh extension create my-extension
```

## Aliases

```bash
gh alias set pv 'pr view'
gh alias set bugs 'issue list --label bug'
gh alias list
gh alias delete pv
gh alias import aliases.yml
```

## JSON Output and Scripting

Most `gh` commands support structured output for scripting:

```bash
gh pr list --json number,title,author --jq '.[] | "\(.number): \(.title)"'
gh issue list --json number,title,labels --jq '.[] | select(.labels | length > 0)'
gh repo list --json name,isPrivate -t '{{range .}}{{.name}}{{"\n"}}{{end}}'
```

Key flags:

- `--json fields` -- output JSON with specified fields
- `--jq expression` -- filter JSON with jq syntax
- `-t, --template` -- format JSON with Go templates
