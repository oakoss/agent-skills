---
title: Creating Skills
description: Skill structure, YAML frontmatter, writing effective descriptions, progressive disclosure, directory conventions, and token efficiency
tags:
  [
    create,
    structure,
    frontmatter,
    description,
    progressive-disclosure,
    directory,
    naming,
  ]
---

# Creating Skills

## Directory Structure

A skill is a directory containing at minimum a `SKILL.md` file:

```sh
skill-name/
├── SKILL.md          # Required: main skill document
├── references/       # Optional: additional documentation loaded on demand
│   ├── basic-patterns.md
│   └── error-handling.md
├── scripts/          # Optional: executable code agents can run
└── assets/           # Optional: templates, images, schemas
```

**Files excluded by the skills CLI during installation** (do not rely on these):

- `README.md`
- `metadata.json`
- Files starting with `_`

## YAML Frontmatter

### Required Fields

```yaml
---
name: my-skill-name
description: |
  What it does in third-person active voice. Key technologies named.

  Use when: scenario one, scenario two, debugging "specific error" messages.
---
```

| Field         | Required | Constraints                                                              |
| ------------- | -------- | ------------------------------------------------------------------------ |
| `name`        | Yes      | 4-64 chars, lowercase letters/numbers/hyphens, must match directory name |
| `description` | Yes      | 1-1024 chars, must include "Use when" or "Use for" trigger phrases       |

### Name Rules

- Lowercase letters, numbers, and hyphens only
- Must not start or end with `-`
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name exactly
- Cannot contain "anthropic" or "claude"

### Optional Fields (Open Standard)

```yaml
---
name: my-skill
description: |
  Skill description here.
license: Apache-2.0
compatibility: Requires git and docker
metadata:
  author: example-org
  version: '1.0'
allowed-tools: Bash(git:*) Read Write
---
```

| Field           | Description                                               |
| --------------- | --------------------------------------------------------- |
| `license`       | License name or reference to bundled file                 |
| `compatibility` | Environment requirements, max 500 chars                   |
| `metadata`      | Arbitrary key-value map (author, version, etc.)           |
| `allowed-tools` | Space-delimited list of pre-approved tools (experimental) |

### Optional Fields (Claude Code Extensions)

| Field                      | Description                                    |
| -------------------------- | ---------------------------------------------- |
| `disable-model-invocation` | Prevent automatic loading, manual `/name` only |
| `user-invocable`           | Set `false` to hide from `/` menu              |
| `model`                    | Model to use when skill is active              |
| `context`                  | Set `fork` to run in a subagent                |
| `agent`                    | Subagent type when `context: fork` is set      |
| `hooks`                    | Hooks scoped to skill lifecycle                |
| `argument-hint`            | Hint for autocomplete (e.g., `[issue-number]`) |

## Writing Effective Descriptions

The description determines if a skill gets discovered. Target 250-350 characters.

### Two-Paragraph Structure

**Paragraph 1**: What you can build + key features (active voice, third person)
**Paragraph 2**: When to use + error keywords for discovery

```yaml
description: |
  Build type-safe database queries with Drizzle ORM and Cloudflare D1.
  Covers schema definition, migrations, relations, and transaction patterns.

  Use when: setting up D1 database, writing Drizzle schemas, debugging
  "no such table" or "D1_ERROR" issues.
```

### Description Checklist

- Active voice ("Builds X" not "This skill provides X")
- Specific technologies named
- 3-5 "Use when" scenarios
- 2-3 distinctive error messages or keywords
- No meta-commentary about the skill itself
- Third-person perspective throughout

### Bad vs Good Descriptions

Bad -- passive, vague, no discovery keywords:

```yaml
description: |
  This skill helps you with database operations. It provides patterns
  for working with data and can be useful in many situations.
```

Good -- active, specific, discoverable:

```yaml
description: |
  Build type-safe database queries with Drizzle ORM and Cloudflare D1.
  Covers schema definition, migrations, relations, and transaction patterns.

  Use when: setting up D1 database, writing Drizzle schemas, debugging
  "no such table" or "D1_ERROR" issues.
```

## Progressive Disclosure

Load information in layers to conserve context window tokens:

| Layer         | When Loaded    | Target Size   | Content                        |
| ------------- | -------------- | ------------- | ------------------------------ |
| **Metadata**  | Always         | ~100 tokens   | name + description             |
| **SKILL.md**  | When triggered | < 5000 tokens | Instructions, patterns, tables |
| **Resources** | As needed      | Variable      | scripts/, references/, assets/ |

Keep SKILL.md under 500 lines. Move detailed reference material to separate files.

## Freedom Levels

Match instruction specificity to error probability:

| Level      | Format                | Use When                                   |
| ---------- | --------------------- | ------------------------------------------ |
| **High**   | Text instructions     | Multiple valid approaches                  |
| **Medium** | Pseudocode/patterns   | Preferred pattern with some flexibility    |
| **Low**    | Exact scripts/configs | Fragile operations where precision matters |

## Token Efficiency

- Move extended examples to `references/` -- keep SKILL.md lean
- One good code example beats three mediocre ones
- Reference official docs instead of copying them
- If the agent already knows it, do not include it

## SKILL.md Required Sections

For this repository, SKILL.md files must include:

1. **YAML frontmatter** with `name` and `description`
2. **Overview** -- 2-3 sentences: what it is, when to use, when NOT to use
3. **Quick Reference** -- table of patterns with API and key points
4. **Common Mistakes** -- table of mistake vs correct pattern
5. **Delegation** -- which agents to use for subtasks
6. **References** -- ordered list of links to `references/*.md`

No code examples belong in SKILL.md. All code lives in reference files.

## Reference File Format

Reference files live at `references/[topic].md` with required frontmatter:

```yaml
---
title: Mutations
description: Mutation patterns, optimistic updates, invalidation strategies
tags: [optimistic, invalidation, mutateAsync, onMutate, rollback]
---
```

Rules for reference files:

- Max 500 lines each (warn at 400)
- Self-contained with code examples
- No cross-references between reference files
- Topic-scoped filenames in kebab-case

## Size Thresholds

| File           | Target        | Warn | Max |
| -------------- | ------------- | ---- | --- |
| SKILL.md       | 100-150 lines | 400  | 500 |
| Reference file | --            | 400  | 500 |

## Validation

Always validate before committing:

```bash
pnpm validate:skills skills/[skill-name]
```

Template skill for reference: `skills/tanstack-query/`
