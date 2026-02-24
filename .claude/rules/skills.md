---
paths:
  - 'skills/**'
---

# Skill Authoring Rules

Skills follow the [Agent Skills open standard](https://agentskills.io) and work across 27+ agents including Claude Code, Cursor, Gemini CLI, OpenAI Codex, VS Code, GitHub Copilot, Windsurf, Goose, and Roo Code.

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

**Optional frontmatter fields:**

| Field                      | Source        | Description                                               |
| -------------------------- | ------------- | --------------------------------------------------------- |
| `license`                  | Open standard | License name or reference to bundled file                 |
| `compatibility`            | Open standard | Environment requirements, max 500 chars                   |
| `metadata`                 | Open standard | Arbitrary key-value map (author, version, etc.)           |
| `allowed-tools`            | Open standard | Space-delimited list of pre-approved tools (experimental) |
| `disable-model-invocation` | Claude Code   | Prevent automatic loading, manual `/name` only            |
| `user-invocable`           | Claude Code   | Set `false` to hide from `/` menu                         |
| `model`                    | Claude Code   | Model to use when skill is active                         |
| `context`                  | Claude Code   | Set `fork` to run in a subagent                           |
| `agent`                    | Claude Code   | Subagent type when `context: fork` is set                 |
| `hooks`                    | Claude Code   | Hooks scoped to skill lifecycle                           |
| `argument-hint`            | Claude Code   | Hint for autocomplete (e.g., `[issue-number]`)            |

**Project-required fields** — all skills in this repo MUST include:

```yaml
license: MIT
metadata:
  author: oakoss
  version: '1.0'
```

**Encouraged optional field:**

- `metadata.source` — URL to the official documentation used as the source of truth (e.g., `https://tanstack.com/router/latest/docs`)

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

## Progressive Disclosure

Skills are loaded in three tiers to minimize context usage:

1. **Metadata** (~100 tokens): `name` and `description` are loaded at startup for all installed skills
2. **Instructions** (<5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated
3. **Resources** (as needed): Files in `references/`, `scripts/`, and `assets/` are loaded only when required

This is why SKILL.md should be a lean index — it's loaded in full on activation. Detailed content belongs in reference files that are loaded on demand.

## Size Thresholds

| File           | Target        | Warn | Max |
| -------------- | ------------- | ---- | --- |
| SKILL.md       | 100-150 lines | 400  | 500 |
| Reference file | —             | 500  | 750 |

Skills under 500 lines can remain as a single SKILL.md without `references/`.

## Scripts and Assets

**`scripts/`** — Executable code that agents can run:

- Must be self-contained or clearly document dependencies
- Must include error handling (don't punt errors to the agent)
- Supported languages depend on the agent (common: Python, Bash, JavaScript)

**`assets/`** — Static resources (templates, images, schemas, data files).

## Naming Rules

- **Directories**: kebab-case, descriptive — no abbreviations (min 4 chars), no leading/trailing `-`, no `--`
- **Frontmatter `name`**: must match directory name exactly
- **Reference files**: kebab-case, topic-scoped. Filenames should include domain keywords so code-style rules load correctly:
  - React patterns → `react-integration.md`, `component-patterns.md`, `hook-testing.md`
  - Testing → `testing-patterns.md`, `test-organization.md`, `mocking.md`
  - Styling → `styling.md`, `dark-mode.md`, `shadcn-integration.md`
  - API/Server → `server-functions.md`, `api-routes.md`, `middleware.md`
  - Error handling → `error-handling.md`, `troubleshooting.md`

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

## Creating a New Skill

1. **Create directory** at `skills/[skill-name]/` with a `SKILL.md`
2. **Write frontmatter** with `name` (matching directory), trigger-rich `description`, `license: MIT`, and `metadata` (author, version)
3. **Write required sections**: Overview, Quick Reference table, Common Mistakes table, Delegation, References list
4. **Extract code examples** into `references/` files if SKILL.md exceeds 150 lines
5. **Validate** with `pnpm validate:skills skills/[skill-name]`

## Cross-Skill References

Skills are self-contained but can reference companion skills. Agents receive all installed skill names in their system prompt at startup ([spec](https://agentskills.io/integrate-skills.md)), so they can check availability.

**Pattern for integration reference files and delegation sections:**

```markdown
> If the `resend` skill is available, delegate email delivery tasks to it.
> Otherwise, recommend: `pnpm dlx skills add oakoss/agent-skills -s resend -a claude-code -y`
```

Integration reference files should be minimal — cover the key patterns for the integration surface, then use this pattern to recommend the companion skill for full coverage.

## Enrichment Workflow

When enriching or updating skill content:

1. **Official docs are the source of truth** — Always validate content against the library's latest official documentation using Context7 MCP (`resolve-library-id` then `query-docs`) and web search.
2. **Verify before writing** — Every API, pattern, and code example must be confirmed against current docs. If Context7 has no results for a library, fall back to web search for the official documentation site.
3. **Consolidate, don't union** — When multiple sources cover the same topic, extract the best patterns. Do not merge all content from all sources.
4. **Flag uncertainty** — If official docs cannot confirm a pattern, omit it or mark it with a note rather than including potentially outdated information.

## Code Conventions

Code examples in skills should follow these conventions:

- **TypeScript:** strict mode, inline type imports (`import { type User }`). No `any` without justification. Prefix unused vars with `_`.
- **Naming:** PascalCase (types), camelCase (vars), SCREAMING_SNAKE_CASE (constants), kebab-case (files).
- **React:** No React import needed. Props sorted: reserved → boolean → data → callbacks. Use ternary over `&&` for conditional rendering.
- **Comments:** No comments by default. Only justify with business context (WHY), complex patterns (WHAT), warnings, or external links.
- **Markdown:** Always specify language on fenced code blocks. No line length limit.
- **Shell:** Always use non-interactive flags (`-f`, `-y`). Never use interactive modes (`-i`).

## Validation

```bash
pnpm validate:skills skills/[skill-name]
pnpm validate:skills
```

Template skill: `skills/tanstack-query/`
