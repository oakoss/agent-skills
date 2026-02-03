---
title: Projects & API
description: GitHub Projects v2 management, REST API, GraphQL API, rulesets, codespaces, and status commands
tags: [gh-cli, projects, api, graphql, rest, rulesets, codespaces, status]
---

# Projects & API

## Projects (v2)

GitHub Projects v2 replaces classic project boards. All `gh project` commands require `--owner` to specify the user or organization.

### List and View

```bash
gh project list --owner @me
gh project list --owner my-org
gh project list --owner @me --json number,title,url
gh project view 1 --owner @me
gh project view 1 --owner @me --web
gh project view 1 --owner @me --json title,items
```

### Create and Edit

```bash
gh project create --owner @me --title "Sprint Board"
gh project edit 1 --owner @me --title "Updated Board"
gh project edit 1 --owner @me --description "Q1 sprint tracking"
gh project close 1 --owner @me
gh project delete 1 --owner @me
gh project copy 1 --source-owner source-org --target-owner @me --title "Copy of Board"
```

### Items

Add issues and PRs to a project:

```bash
gh project item-add 1 --owner @me --url https://github.com/owner/repo/issues/123
gh project item-create 1 --owner @me --title "Draft item"
gh project item-list 1 --owner @me
gh project item-list 1 --owner @me --json id,title,status
gh project item-archive 1 --owner @me --id ITEM_ID
gh project item-delete 1 --owner @me --id ITEM_ID
```

### Edit Item Fields

```bash
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --text "value"
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --single-select-option-id OPTION_ID
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --date "2025-01-15"
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --number 5
gh project item-edit --project-id PROJECT_ID --id ITEM_ID --field-id FIELD_ID --clear
```

### Fields

```bash
gh project field-list 1 --owner @me
gh project field-create 1 --owner @me --name "Priority" --data-type SINGLE_SELECT --single-select-options "Low,Medium,High"
gh project field-create 1 --owner @me --name "Due Date" --data-type DATE
gh project field-create 1 --owner @me --name "Story Points" --data-type NUMBER
gh project field-delete 1 --owner @me --id FIELD_ID
```

Field data types: `TEXT`, `SINGLE_SELECT`, `DATE`, `NUMBER`.

### Link and Unlink

Link a project to a repository:

```bash
gh project link 1 --owner @me --repo owner/repo
gh project unlink 1 --owner @me --repo owner/repo
```

### Templates

```bash
gh project mark-template 1 --owner @me
```

## REST API

```bash
gh api repos/owner/repo
gh api repos/owner/repo/issues
gh api repos/owner/repo/issues -f title="New issue" -f body="Description"
gh api repos/owner/repo/pulls/45/comments
gh api repos/owner/repo --jq '.stargazers_count'
gh api repos/owner/repo/issues --paginate
gh api repos/owner/repo -X PATCH -f description="Updated"
gh api repos/owner/repo/actions/caches --paginate --jq '.actions_caches[].key'
```

Key flags:

- `-X, --method` -- HTTP method (GET, POST, PATCH, DELETE)
- `-f, --field` -- add a string field
- `-F, --raw-field` -- add a raw field (for numbers, booleans, null)
- `--paginate` -- fetch all pages of results
- `--jq` -- filter response with jq
- `-t, --template` -- format output with Go template
- `--hostname` -- target a GitHub Enterprise host
- `-H, --header` -- add custom HTTP headers
- `--input` -- read body from file

## GraphQL API

```bash
gh api graphql -f query='{ viewer { login } }'

gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      issues(first: 10, states: OPEN) {
        nodes { number title }
      }
    }
  }
' -f owner="owner" -f repo="repo"

gh api graphql --paginate -f query='
  query($endCursor: String) {
    viewer {
      repositories(first: 100, after: $endCursor) {
        nodes { nameWithOwner }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
'
```

## Rulesets

View and check repository rulesets:

```bash
gh ruleset list
gh ruleset list --org my-org
gh ruleset view 1
gh ruleset check --branch main
```

## Codespaces

```bash
gh codespace list
gh codespace create --repo owner/repo
gh codespace create --repo owner/repo --machine largePremiumLinux
gh codespace ssh -c CODESPACE_NAME
gh codespace code -c CODESPACE_NAME
gh codespace stop -c CODESPACE_NAME
gh codespace delete -c CODESPACE_NAME
gh codespace ports -c CODESPACE_NAME
gh codespace logs -c CODESPACE_NAME
```

## Status

View notifications, assigned issues, and review requests:

```bash
gh status
gh status --org my-org
```

## Organization

```bash
gh org list
```
