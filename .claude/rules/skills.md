---
paths:
  - 'skills/**'
---

# Skill Authoring Rules

Skills follow the [Agent Skills open standard](https://agentskills.io).

## Directory Structure

```text
skill-name/
├── SKILL.md          # Lean index (100-150 lines, no code examples)
├── references/       # Additional documentation loaded on demand
│   ├── basic-patterns.md
│   ├── error-handling.md
│   └── ...
├── scripts/          # Executable code agents can run
└── assets/           # Templates, images, schemas
```

## SKILL.md Frontmatter

**Required fields:**

| Field         | Constraints                                                                                                                                                   |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`        | Lowercase letters, numbers, hyphens. 4-64 chars. Must match directory. No leading/trailing `-`, no `--`. Cannot contain "anthropic" or "claude". No XML tags. |
| `description` | 1-1024 chars. Third-person voice. Must include "Use when..." or "Use for..." triggers. No XML tags.                                                           |

**Optional fields (open standard):** `license`, `compatibility` (max 500 chars), `metadata` (key-value map), `allowed-tools` (experimental).

**Optional fields (Claude Code):** `disable-model-invocation`, `user-invocable`, `model`, `context`, `agent`, `hooks`, `argument-hint`.

## SKILL.md Required Sections

1. **YAML frontmatter** — `name` and `description`
2. **Overview** — 2-3 sentences: what it is, when to use, when NOT to use
3. **Quick Reference** — Table of patterns with API and key points
4. **Common Mistakes** — Table of mistake vs correct pattern
5. **Delegation** — Which agents to use for discovery, review, etc.
6. **References** — Ordered list of links to `references/*.md`

**No code examples in SKILL.md** — all code lives in `references/`.

## Reference Files

- Located at `references/[topic].md`, kebab-case filenames
- Max 500 lines each (warn at 400)
- Self-contained with code examples, no cross-references between files
- Topic-scoped (e.g., `mutations.md` not `mut-optimistic-updates.md`)

Required frontmatter:

```yaml
---
title: Mutations
description: Mutation patterns, optimistic updates, invalidation strategies
tags: [optimistic, invalidation, mutateAsync, onMutate, rollback]
---
```

## Size Thresholds

| File           | Target        | Warn | Max |
| -------------- | ------------- | ---- | --- |
| SKILL.md       | 100-150 lines | 400  | 500 |
| Reference file | —             | 400  | 500 |

## Naming Rules

- **Directories**: kebab-case, descriptive — no abbreviations (min 4 chars), no leading/trailing `-`, no `--`
- **Frontmatter `name`**: must match directory name exactly
- **Reference files**: kebab-case, topic-scoped

## Content Guidelines

- **Third-person descriptions**: "Extracts text from PDFs", not "I help you" or "Use this to"
- **No time-sensitive info**: use "current method" and "legacy" sections instead of dates
- **Consistent terminology**: pick one term and use it throughout
- **Forward slashes only** in file paths
- **Scripts handle errors**: bundled scripts must handle errors explicitly
- **One level deep**: reference files link directly from SKILL.md, no nested references

## Distribution Compatibility

The Vercel `skills` CLI excludes these files during installation — do not use them in skill directories:

- `README.md`
- `metadata.json`
- Files starting with `_`

## Validation

```bash
pnpm validate:skills skills/[skill-name]
pnpm validate:skills
```

Template skill: `skills/tanstack-query/`
