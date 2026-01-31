---
title: Issues
description: GitHub CLI issue creation, listing, editing, closing, commenting, labeling, pinning, transferring, and development branches
tags: [gh-cli, issues, labels, assignments, pin, transfer, develop]
---

# Issues

## List and Filter

```bash
gh issue list
gh issue list --state closed
gh issue list --label "bug" --assignee @me
gh issue list --milestone "v2.0"
gh issue list --search "memory leak in:title"
gh issue list --limit 50
gh issue list --json number,title,state,labels
```

## View

```bash
gh issue view 123
gh issue view 123 --web
gh issue view 123 --json title,body,comments
gh issue view 123 --comments
```

## Create

```bash
gh issue create --title "Bug: Login fails" --body "Steps to reproduce..."
gh issue create --title "Feature request" --label "enhancement" --assignee @me
gh issue create --title "Task" --project "Sprint Board"
gh issue create --body-file issue-body.md --title "Detailed issue"
gh issue create
```

The interactive mode (no flags) prompts for title, body, labels, assignees, projects, and milestones.

## Edit

```bash
gh issue edit 123 --title "Updated title"
gh issue edit 123 --body "Updated description"
gh issue edit 123 --add-assignee @me
gh issue edit 123 --remove-assignee user1
gh issue edit 123 --add-label "bug,priority:high"
gh issue edit 123 --remove-label "wontfix"
gh issue edit 123 --add-project "Sprint Board"
gh issue edit 123 --milestone "v2.0"
```

## Close and Reopen

```bash
gh issue close 123
gh issue close 123 --reason "not planned"
gh issue close 123 --reason completed --comment "Fixed in PR #456"
gh issue reopen 123
```

Close reasons: `completed`, `not planned`.

## Comment

```bash
gh issue comment 123 --body "Working on this"
gh issue comment 123 --body-file comment.md
gh issue comment 123 --web
```

## Pin and Unpin

```bash
gh issue pin 123
gh issue unpin 123
```

## Transfer

Move an issue to another repository:

```bash
gh issue transfer 123 owner/other-repo
```

## Lock and Unlock

```bash
gh issue lock 123 --reason "resolved"
gh issue unlock 123
```

Lock reasons: `off-topic`, `too heated`, `resolved`, `spam`.

## Develop (Create Branch from Issue)

Create a development branch linked to an issue:

```bash
gh issue develop 123
gh issue develop 123 --base main
gh issue develop 123 --name "fix/login-bug"
gh issue develop 123 --checkout
```

## Delete

```bash
gh issue delete 123 --yes
```

## Status

View issues relevant to you across repositories:

```bash
gh issue status
```

## Labels

```bash
gh label list
gh label create "priority:high" --color FF0000 --description "High priority"
gh label create "area:auth" --color 0075ca
gh label edit "bug" --color 00FF00 --description "Something is broken"
gh label delete "wontfix" --yes
gh label clone --from owner/source-repo
```
