---
title: Private Repositories
description: Installing skills from private GitHub and GitLab repositories using SSH URLs and credential configuration
tags: [private, ssh, authentication, credentials, github, gitlab]
---

# Private Repositories

## The Problem

The `owner/repo` shorthand converts to an HTTPS URL internally. For private repos, this triggers the system credential helper, which often results in an endless spinner (the git credential prompt is hidden) or a "Repository not found" error.

## Recommended: Use SSH URLs

The most reliable method for private repos is passing an SSH URL directly:

```bash
# GitHub private repo
pnpm dlx skills add git@github.com:YourOrg/private-skills.git -y

# GitHub private repo — specific skill
pnpm dlx skills add git@github.com:YourOrg/private-skills.git --skill my-skill -y

# GitHub private repo — global install
pnpm dlx skills add git@github.com:YourOrg/private-skills.git --skill my-skill -g -y

# GitLab private repo
pnpm dlx skills add git@gitlab.com:YourOrg/private-skills.git -y

# List available skills in a private repo
pnpm dlx skills add git@github.com:YourOrg/private-skills.git --list
```

This works because SSH uses existing key-based authentication rather than HTTPS credentials.

### Prerequisites

The user must have SSH keys configured for their git host:

```bash
# Verify SSH access to GitHub
ssh -T git@github.com

# Verify SSH access to GitLab
ssh -T git@gitlab.com
```

If SSH is not configured, the user needs to set up an SSH key and add it to their git host account.

## Alternative: Configure HTTPS Credentials

If SSH is not available, pre-configure git credentials before running the skills CLI:

```bash
# Option 1: Use gh CLI (recommended if available)
gh auth setup-git

# Option 2: Store a personal access token
git config --global credential.helper store
# Then authenticate once — credentials are cached for future use
```

After configuring credentials, the `owner/repo` shorthand works normally:

```bash
pnpm dlx skills add YourOrg/private-skills --skill my-skill -y
```

## Known Limitations

### `skills check` and `skills update` Do Not Work

The CLI makes unauthenticated GitHub API calls to detect skill updates. For private repos, these return 404, so:

- `pnpm dlx skills check` always shows "skipped (reinstall needed)"
- `pnpm dlx skills update` cannot update private repo skills

**Workaround:** Reinstall the skill to update it:

```bash
pnpm dlx skills add git@github.com:YourOrg/private-skills.git --skill my-skill -y
```

### Spinner Hides Credential Prompts

If the CLI appears stuck during "Cloning repository," it may be waiting for credential input hidden behind the spinner. Kill the process and retry with an SSH URL instead.

## Troubleshooting

| Symptom                                 | Cause                                       | Fix                                          |
| --------------------------------------- | ------------------------------------------- | -------------------------------------------- |
| Endless spinner on clone                | Credential prompt hidden behind spinner     | Use SSH URL instead                          |
| "Repository not found"                  | No HTTPS credentials cached                 | Use SSH URL or configure `gh auth setup-git` |
| "Permission denied (publickey)"         | SSH key not configured or not added to host | Run `ssh -T git@github.com` to diagnose      |
| Updates always show "skipped"           | Unauthenticated API calls return 404        | Reinstall the skill manually                 |
| Works for some team members, not others | Different credential helper configs         | Standardize on SSH URLs across the team      |
