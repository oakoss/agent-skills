---
title: Discovery Guide
description: Step-by-step workflow for discovering and installing agent skills, with CLI reference and agent targeting
tags: [discovery, search, install, workflow, skills-cli, claude-code, agents]
---

# Discovery Guide

## When to Activate

Activate skill discovery when the user:

- Asks "how do I do X" where X might have an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain

## Step-by-Step Workflow

### Step 1: Understand What They Need

Identify three things before searching:

1. **The domain** — React, testing, design, deployment, etc.
2. **The specific task** — writing tests, creating animations, reviewing PRs
3. **Likelihood a skill exists** — common tasks in popular domains usually have skills

### Step 2: Search for Skills

Run the find command with a relevant query:

```bash
pnpm dlx skills find [query]
```

Example mappings from user requests to search queries:

| User Says                            | Search Query                             |
| ------------------------------------ | ---------------------------------------- |
| "How do I make my React app faster?" | `pnpm dlx skills find react performance` |
| "Can you help me with PR reviews?"   | `pnpm dlx skills find pr review`         |
| "I need to create a changelog"       | `pnpm dlx skills find changelog`         |
| "Help me write better tests"         | `pnpm dlx skills find testing`           |
| "I want to set up CI/CD"             | `pnpm dlx skills find ci-cd deploy`      |

For richer results with descriptions, use the enrichment script:

```bash
node scripts/enrich_find.js "react performance"
```

### Step 3: Present Options to the User

When results are found, present each skill with:

1. The skill name and what it does
2. The install command (defaulting to Claude Code as the target agent)
3. A link to learn more on skills.sh

Example response format:

```text
I found a skill that might help! The "react-best-practices" skill provides
React performance optimization guidelines.

To install it:
pnpm dlx skills add vercel-labs/agent-skills -s react-best-practices -a claude-code -y

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### Step 4: Offer to Install

If the user wants to proceed, install with confirmation bypass. Default to Claude Code as the target agent:

```bash
pnpm dlx skills add <source> -s <name> -a claude-code -y
```

For global (user-level) install:

```bash
pnpm dlx skills add <source> -s <name> -a claude-code -g -y
```

- `-a claude-code` targets Claude Code specifically
- `-g` installs at user level (available across projects)
- `-y` skips interactive confirmation

## Agent Targeting

The `-a` flag controls which agent(s) receive the skill. Always specify the target agent explicitly.

**Default agent:** `claude-code`

To install for multiple agents, pass multiple names:

```bash
pnpm dlx skills add <source> -s <name> -a claude-code opencode github-copilot -y
```

To install for all detected agents:

```bash
pnpm dlx skills add <source> -s <name> -a '*' -y
```

Common agent identifiers (full list at `github.com/vercel-labs/skills`):

| Agent          | CLI Name         |
| -------------- | ---------------- |
| Claude Code    | `claude-code`    |
| OpenCode       | `opencode`       |
| GitHub Copilot | `github-copilot` |
| Cursor         | `cursor`         |
| Windsurf       | `windsurf`       |
| Gemini CLI     | `gemini-cli`     |
| Codex          | `codex`          |
| Roo Code       | `roo`            |
| Cline          | `cline`          |
| Goose          | `goose`          |
| Amp            | `amp`            |

## CLI Reference

### Commands

| Command               | Description                     |
| --------------------- | ------------------------------- |
| `skills add <source>` | Install skills from a source    |
| `skills remove`       | Remove installed skills         |
| `skills list`         | List installed skills           |
| `skills find [query]` | Search for skills interactively |
| `skills init [name]`  | Scaffold a new skill            |
| `skills check`        | Check for available updates     |
| `skills update`       | Update all installed skills     |

### Add Options

| Flag               | Short | Description                                    |
| ------------------ | ----- | ---------------------------------------------- |
| `--global`         | `-g`  | Install at user level instead of project       |
| `--agent <agents>` | `-a`  | Target specific agents (default: all detected) |
| `--skill <skills>` | `-s`  | Install specific skills from the source        |
| `--list`           | `-l`  | List available skills without installing       |
| `--yes`            | `-y`  | Skip confirmation prompts                      |
| `--all`            |       | Shorthand for `-s '*' -a '*' -y`               |
| `--full-depth`     |       | Search all subdirectories for skills           |

### Remove Options

| Flag               | Short | Description                      |
| ------------------ | ----- | -------------------------------- |
| `--global`         | `-g`  | Remove from global scope         |
| `--agent <agents>` | `-a`  | Remove from specific agents      |
| `--skill <skills>` | `-s`  | Remove specific skills           |
| `--yes`            | `-y`  | Skip confirmation prompts        |
| `--all`            |       | Shorthand for `-s '*' -a '*' -y` |

### List Options

| Flag               | Short | Description                           |
| ------------------ | ----- | ------------------------------------- |
| `--global`         | `-g`  | List global skills (default: project) |
| `--agent <agents>` | `-a`  | Filter by specific agents             |

### Source Formats

The `<source>` argument accepts multiple formats:

| Format                  | Example                           |
| ----------------------- | --------------------------------- |
| GitHub shorthand        | `vercel-labs/agent-skills`        |
| GitHub URL              | `https://github.com/owner/repo`   |
| GitLab URL              | `https://gitlab.com/owner/repo`   |
| SSH URL (private repos) | `git@github.com:Org/repo.git`     |
| Any git URL             | `https://example.com/repo.git`    |
| Local path              | `./my-skills` or `/absolute/path` |

## Search Tips

1. **Use specific keywords** — "react testing" beats just "testing"
2. **Try alternative terms** — if "deploy" returns nothing, try "deployment" or "ci-cd"
3. **Check popular sources** — many skills come from `vercel-labs/agent-skills` or `oakoss/agent-skills`
4. **Browse the catalog** — `https://skills.sh/` shows curated listings
5. **Combine domain + task** — "typescript validation", "nextjs auth", "react forms"
6. **Preview before installing** — use `--list` to see available skills in a repo

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using general capabilities
3. Suggest creating a custom skill if the task is recurring

```text
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly. Would you like me to proceed?

If this is something you do often, you could create your own skill:
pnpm dlx skills init my-xyz-skill
```

## Skill Sources

| Source            | Description                                     |
| ----------------- | ----------------------------------------------- |
| `skills.sh`       | Web catalog with descriptions and install links |
| `agent-skills.md` | Fallback documentation source                   |
| GitHub repos      | Skills are hosted in GitHub repositories        |

Skills follow the [Agent Skills open standard](https://agentskills.io) and work across 27+ agents including Claude Code, Cursor, Gemini CLI, and others.
