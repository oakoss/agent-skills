---
title: Issues
description: GitHub CLI issue creation, listing, closing, commenting, assigning, labeling, and project management
tags: [gh-cli, issues, labels, projects, assignments]
---

# Issues

## Issue Commands

```bash
gh issue list
gh issue create --title "Bug: Login fails" --body "Description here"
gh issue create  # interactive
gh issue view 123
gh issue close 123
gh issue reopen 123
gh issue comment 123 --body "Working on this"
```

## Edit Issues

```bash
gh issue edit 123 --add-assignee @me
gh issue edit 123 --add-label "bug,priority:high"
```

## Labels

```bash
gh label list
gh label create "priority:high" --color FF0000 --description "High priority"
```

## Projects

```bash
gh project list
gh project view 1
```
