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

## Skills

Skills in `skills/` follow the [Agent Skills open standard](https://agentskills.io). Detailed authoring rules, validation, and conventions are in `.claude/rules/skills.md`.

Quick commands:

- `pnpm validate:skills` — validate all skills
- `pnpm validate:skills skills/[name]` — validate one skill
- Template skill: `skills/tanstack-query/`
