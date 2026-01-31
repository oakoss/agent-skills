# Agent Instructions

<!-------------------------------------Beads-------------------------------------------------->

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:

   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```

5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**

- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

<!-------------------------------------Beads End----------------------------------------------------->

## Project Overview

Agent skills, distributed via Vercel's `skills` CLI (`pnpm dlx skills add oakoss/agent-skills`).

- **`skills/`** — Public skills distributed to users

## Commands

```sh
pnpm format          # Prettier (single quotes, auto-sort package.json)
pnpm format:check    # Check formatting without writing
pnpm lint            # markdownlint-cli2 on all .md files
pnpm lint:fix        # Lint and auto-fix markdown
pnpm validate:skills # Validate all skills in skills/
```

Git hooks (via lefthook) run markdown lint + prettier on pre-commit and commitlint on commit-msg.

## Commit Conventions

Conventional commits enforced by commitlint. Max header: 200 chars. Valid scopes: `skills`, `validator`, `docs`, `config`, `deps`, `ci`. Aliases: `fd` (docs fix), `b` (bump deps).

## Skill Standards

Skills follow the [Agent Skills open standard](https://agentskills.io) and work across 27+ agents including Claude Code, Cursor, Gemini CLI, OpenAI Codex, VS Code, GitHub Copilot, Windsurf, Goose, and Roo Code.

### Directory Structure

```sh
skill-name/
├── SKILL.md          # Lean index (100-150 lines, no code examples)
├── references/       # Optional: additional documentation loaded on demand
│   ├── basic-patterns.md
│   ├── error-handling.md
│   └── ...
├── scripts/          # Optional: executable code agents can run
└── assets/           # Optional: templates, images, schemas
```

### SKILL.md Requirements

**Frontmatter** (required):

```yaml
---
name: skill-name
description: 'What it does. Use when X, Y, Z. Use for keyword1, keyword2, keyword3.'
---
```

- `name` — lowercase letters, numbers, and hyphens only. 4-64 chars. Must match directory name. Must not start/end with `-` or contain `--`. Cannot contain "anthropic" or "claude". No XML tags.
- `description` — third-person voice ("Extracts text from PDFs", not "I help you" or "Use this to"). Must include "Use when..." or "Use for..." trigger phrases. Max 1024 chars. No XML tags.

**Optional frontmatter fields**:

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

**Project-required frontmatter** — all skills in this repo MUST include:

```yaml
---
name: skill-name
description: 'What it does. Use when X, Y, Z. Use for keyword1, keyword2, keyword3.'
license: MIT
metadata:
  author: oakoss
  version: '1.0'
---
```

- `license: MIT` — all skills in this repo are MIT licensed
- `metadata.author: oakoss` — identifies the skill author/org
- `metadata.version` — tracks skill content version (bump on significant changes)

**Required sections**: Overview, Quick Reference table, Common Mistakes table, Delegation, References list.

**No code examples in SKILL.md** — all code lives in `references/`.

### Reference Files

- Located at `references/[topic].md`, kebab-case filenames
- Max 500 lines each (warn at 400)
- Required frontmatter: `title`, `description`, `tags`
- Self-contained with code examples, no cross-references between files
- Topic-scoped (e.g., `mutations.md` not `mut-optimistic-updates.md`)

### Progressive Disclosure

Skills are loaded in three tiers to minimize context usage:

1. **Metadata** (~100 tokens): `name` and `description` are loaded at startup for all installed skills
2. **Instructions** (<5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated
3. **Resources** (as needed): Files in `references/`, `scripts/`, and `assets/` are loaded only when required

This is why SKILL.md should be a lean index — it's loaded in full on activation. Detailed content belongs in reference files that are loaded on demand.

### Size Thresholds

| File           | Target        | Warn | Max |
| -------------- | ------------- | ---- | --- |
| SKILL.md       | 100-150 lines | 400  | 500 |
| Reference file | —             | 400  | 500 |

Skills under 500 lines can remain as a single SKILL.md without `references/`.

### Scripts and Assets

**`scripts/`** — Executable code that agents can run:

- Must be self-contained or clearly document dependencies
- Must include error handling (don't punt errors to the agent)
- Supported languages depend on the agent (common: Python, Bash, JavaScript)

**`assets/`** — Static resources (templates, images, schemas, data files).

### Naming Rules

- **Directories**: kebab-case, descriptive — no abbreviations (min 4 chars), no leading/trailing `-`, no `--`
- **Frontmatter `name`**: must match directory name exactly (lowercase letters, numbers, hyphens only)
- **Reference files**: kebab-case, topic-scoped

### Distribution Compatibility

Skills are installed via Vercel's `skills` CLI. The CLI excludes these files during installation — do not use them in skill directories:

- `README.md`
- `metadata.json`
- Files starting with `_`

### Validation

Run `pnpm validate:skills` before committing. The validator checks: frontmatter fields, name length/format, description triggers, line counts, code block language specifiers, required sections, reference link integrity, and CLI-excluded filenames.

Template skill: `tanstack-query/` (lean SKILL.md + 13 reference files).

### Creating a New Skill

1. **Create directory** at `skills/[skill-name]/` with a `SKILL.md`
2. **Write frontmatter** with `name` (matching directory), trigger-rich `description`, `license: MIT`, and `metadata` (author, version)
3. **Write required sections**: Overview, Quick Reference table, Common Mistakes table, Delegation, References list
4. **Extract code examples** into `references/` files if SKILL.md exceeds 150 lines
5. **Validate** with `pnpm validate:skills skills/[skill-name]`

## Content Guidelines

- **No time-sensitive info** — avoid "as of 2025" or "before version X". Use "current method" and "legacy" sections instead.
- **Consistent terminology** — pick one term and use it throughout (e.g., always "endpoint", not a mix of "endpoint", "route", "URL").
- **Forward slashes only** in file paths (`reference/guide.md`, not `reference\guide.md`).
- **Scripts handle errors** — scripts bundled in skills should handle errors explicitly, not punt to Claude.
- **One level deep** — reference files link directly from SKILL.md, no nested references between files.

## Code Conventions

Code examples in skills should follow these conventions:

- **TypeScript:** strict mode, inline type imports (`import { type User }`). No `any` without justification. Prefix unused vars with `_`.
- **Naming:** PascalCase (types), camelCase (vars), SCREAMING_SNAKE_CASE (constants), kebab-case (files).
- **React:** No React import needed. Props sorted: reserved → boolean → data → callbacks. Use ternary over `&&` for conditional rendering.
- **Comments:** No comments by default. Only justify with business context (WHY), complex patterns (WHAT), warnings, or external links.
- **Markdown:** Always specify language on fenced code blocks. No line length limit.
- **Shell:** Always use non-interactive flags (`-f`, `-y`). Never use interactive modes (`-i`).
