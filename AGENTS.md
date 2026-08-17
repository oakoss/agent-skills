# Agent Instructions

<!-------------------------------------Beads-------------------------------------------------->

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Export beads to JSONL for git
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

Agent skills, distributed via Vercel's `skills` CLI (`pnpm dlx skills add oakoss/agent-skills`). This project uses **pnpm** as the package manager.

- **`skills/`** — Public skills distributed to users

## Commands

```sh
pnpm format          # Prettier (single quotes, auto-sort package.json)
pnpm format:check    # Check formatting without writing
pnpm lint            # markdownlint-cli2 on all .md files
pnpm lint:fix        # Lint and auto-fix markdown
pnpm validate:skills # Validate all skills in skills/
```

## Commit Conventions

Conventional commits enforced by commitlint. Max header: 200 chars. Scopes restricted to: `skills`, `validator`, `docs`, `config`, `deps`, `ci`. Aliases: `fd` (docs fix), `b` (bump deps).

## Node Version

This project requires the Node.js version specified in `.nvmrc`.

## Git Hooks

[Lefthook](https://github.com/evilmartians/lefthook) runs these hooks automatically:

| Hook                 | What runs                                                            |
| -------------------- | -------------------------------------------------------------------- |
| `pre-commit`         | markdownlint (auto-fix), Prettier (auto-fix), skill validator, beads |
| `commit-msg`         | commitlint                                                           |
| `prepare-commit-msg` | beads                                                                |
| `post-merge`         | beads                                                                |
| `post-checkout`      | beads                                                                |
| `pre-push`           | beads                                                                |

Lefthook owns every git hook. Beads must not install its own — `bd init` and
`bd hooks install` both set `core.hooksPath` to `.beads/hooks`, which silently
bypasses lefthook. Beads is invoked through `.lefthook/bd-hook.sh` instead.

Pre-commit hooks auto-stage fixes, so markdown lint and Prettier corrections are included in the commit automatically. If the skill validator or commitlint fails, the commit is rejected — fix the issue and commit again.

## Plan Mode

- Make plans extremely concise. Sacrifice grammar for concision.
- End each plan with a list of unresolved questions, if any.

## Code Style Rules

`.claude/rules/` contains coding convention rules scoped to skill reference files. These ensure code examples follow consistent patterns (TypeScript strict mode, React conventions, testing patterns, etc.). Rules use glob-based path scoping — they only load when editing files that match by skill name or reference filename.

## Skills

Skills in `skills/` follow the [Agent Skills open standard](https://agentskills.io). Detailed authoring rules, validation, and conventions are in `.claude/rules/skills.md`.

Quick commands:

- `pnpm validate:skills` — validate all skills
- `pnpm validate:skills skills/[name]` — validate one skill
- Template skill: `skills/tanstack-query/`

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:970c3bf2 -->

## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See <https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md> for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:

   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status
   ```

5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**

- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->

<!-- BEGIN BEADS CODEX SETUP: generated by bd setup codex -->

## Beads Issue Tracker

Use Beads (`bd`) for durable task tracking in repositories that include it. Use the `beads` skill at `.agents/skills/beads/SKILL.md` (project install) or `~/.agents/skills/beads/SKILL.md` (global install) for Beads workflow guidance, then use the `bd` CLI for issue operations.

### Quick Reference

```bash
bd ready                # Find available work
bd show <id>            # View issue details
bd update <id> --claim  # Claim work
bd close <id>           # Complete work
bd prime                # Refresh Beads context
```

### Rules

- Use `bd` for all task tracking; do not create markdown TODO lists.
- Run `bd prime` when Beads context is missing or stale. Codex 0.129.0+ can load Beads context automatically through native hooks; use `/hooks` to inspect or toggle them.
- Keep persistent project memory in Beads via `bd remember`; do not create ad hoc memory files.

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See <https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md> for details and anti-patterns.

<!-- END BEADS CODEX SETUP -->
