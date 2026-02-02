---
title: Discovery Guide
description: Step-by-step workflow for discovering and installing agent skills from the open ecosystem
tags: [discovery, search, install, workflow, skills-cli]
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
2. The install command
3. A link to learn more on skills.sh

Example response format:

```text
I found a skill that might help! The "react-best-practices" skill provides
React performance optimization guidelines.

To install it:
pnpm dlx skills add vercel-labs/agent-skills --skill react-best-practices -y

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### Step 4: Offer to Install

If the user wants to proceed, install with confirmation bypass:

```bash
pnpm dlx skills add <owner/repo> --skill <name> -g -y
```

- `-g` installs at user level (available across projects)
- `-y` skips interactive confirmation

## Search Tips

1. **Use specific keywords** — "react testing" beats just "testing"
2. **Try alternative terms** — if "deploy" returns nothing, try "deployment" or "ci-cd"
3. **Check popular sources** — many skills come from `vercel-labs/agent-skills` or `oakoss/agent-skills`
4. **Browse the catalog** — `https://skills.sh/` shows curated listings
5. **Combine domain + task** — "typescript validation", "nextjs auth", "react forms"

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
