---
title: Skill Anatomy
description: Directory structure, SKILL.md required sections, progressive disclosure tiers, size thresholds, and file organization
tags:
  [
    directory,
    structure,
    progressive-disclosure,
    size,
    references,
    scripts,
    assets,
  ]
---

# Skill Anatomy

## Directory Structure

A skill is a directory containing at minimum a `SKILL.md` file:

```sh
skill-name/
├── SKILL.md          # Required: lean index with frontmatter + instructions
├── references/       # Optional: additional documentation loaded on demand
│   ├── basic-patterns.md
│   ├── error-handling.md
│   └── advanced-config.md
├── scripts/          # Optional: executable code agents can run
│   └── validate.py
└── assets/           # Optional: templates, images, schemas, data files
    └── config-template.json
```

## SKILL.md Required Sections

Every SKILL.md must include these sections:

### 1. YAML Frontmatter

The file must start with a `---` delimited YAML block on line 1 (no blank lines before it):

```yaml
---
name: my-skill
description: 'What it does. Use when X, Y, Z. Use for keyword1, keyword2.'
---
```

### 2. Overview

Two to three sentences covering what the skill does, when to use it, and optionally when NOT to use it:

```markdown
## Overview

TanStack Query is an async state manager, not a data fetching library. You provide a `queryFn` that returns a Promise; it handles caching, deduplication, and background updates.
```

### 3. Quick Reference Table

A table summarizing the most important patterns, APIs, or concepts:

```markdown
## Quick Reference

| Pattern        | API                               | Key Points            |
| -------------- | --------------------------------- | --------------------- |
| Basic query    | `useQuery({ queryKey, queryFn })` | Include params in key |
| Basic mutation | `useMutation({ mutationFn })`     | Invalidate on success |
```

### 4. Common Mistakes Table

A table of frequent errors paired with correct patterns:

```markdown
## Common Mistakes

| Mistake                  | Correct Pattern            |
| ------------------------ | -------------------------- |
| Inline queryFn in render | Extract to stable function |
| Missing error handling   | Always check error state   |
```

### 5. Delegation

Which agents or tools to use for subtasks:

```markdown
## Delegation

- **Pattern discovery**: Use `Explore` agent
- **Code review**: Delegate to `code-reviewer` agent
```

### 6. References List

Ordered list of links to reference files with descriptive text:

```markdown
## References

- [Basic patterns and architecture](references/basic-patterns.md)
- [Error handling strategies](references/error-handling.md)
```

## Progressive Disclosure

Skills are loaded in three tiers to minimize context usage:

### Tier 1: Metadata (~100 tokens)

The `name` and `description` fields are loaded at startup for all installed skills. This is how agents decide which skill to activate for a given task.

### Tier 2: Instructions (<5000 tokens recommended)

The full `SKILL.md` body is loaded when the skill is activated. This is why SKILL.md should be a lean index -- it is loaded in full on activation. Keep it under 150 lines.

### Tier 3: Resources (as needed)

Files in `references/`, `scripts/`, and `assets/` are loaded only when required. Agents discover these files through explicit links in SKILL.md.

```text
User asks about PDFs
  → Agent scans skill descriptions (Tier 1)
  → Activates pdf-processing skill, loads SKILL.md (Tier 2)
  → Reads references/form-filling.md for the specific task (Tier 3)
```

## Size Thresholds

| File           | Target        | Warn | Max |
| -------------- | ------------- | ---- | --- |
| SKILL.md       | 100-150 lines | 400  | 500 |
| Reference file | Varies        | 400  | 500 |

When SKILL.md exceeds 150 lines, extract detailed content into reference files. When a reference file exceeds 400 lines, consider splitting it into multiple topic-scoped files.

## Reference Files

Reference files live in `references/` and follow these rules:

- **Filename**: kebab-case, topic-scoped (e.g., `mutations.md`, not `mut-optimistic-updates.md`)
- **Frontmatter**: Required `title`, `description`, and `tags` fields
- **Self-contained**: Each file includes its own code examples and context
- **No cross-references**: Reference files do not link to each other
- **One level deep**: SKILL.md links to references directly, no nested chains

Reference file frontmatter example:

```yaml
---
title: Error Handling
description: Error boundary integration, retry strategies, and fallback patterns
tags: [error-boundary, retry, fallback, throwOnError]
---
```

## Scripts Directory

Scripts in `scripts/` execute without loading source into context. Only their output consumes tokens.

Use scripts for:

- Complex validation logic that is verbose to describe in prose
- Data processing that is more reliable as tested code
- Operations that benefit from consistency across uses

In SKILL.md, instruct the agent to **run** the script (not read it):

```markdown
Run the validation script:

scripts/validate.py path/to/check
```

Scripts must:

- Be self-contained or clearly document dependencies
- Include error handling (do not punt errors to the agent)
- Be executable (`chmod +x`)

## Assets Directory

The `assets/` directory holds static resources: templates, images, schemas, and data files. These are loaded on demand when referenced from SKILL.md or reference files.

## Naming Rules

| Element          | Convention                                                         |
| ---------------- | ------------------------------------------------------------------ |
| Skill directory  | kebab-case, min 4 chars, no abbreviations, no leading/trailing `-` |
| Frontmatter name | Must match directory name exactly                                  |
| Reference files  | kebab-case, topic-scoped                                           |

## Distribution Compatibility

When distributing via the Vercel `skills` CLI, these files are excluded during installation and must not be used for skill content:

- `README.md`
- `metadata.json`
- Files starting with `_`

## Cross-Skill References

Skills are self-contained but can reference companion skills. Agents receive all installed skill names at startup, so they can check availability:

```markdown
> If the `resend` skill is available, delegate email delivery tasks to it.
> Otherwise, recommend: `npx skills add oakoss/agent-skills --skill resend`
```
