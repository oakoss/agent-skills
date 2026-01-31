---
title: Conventional Commits
description: Commit message format, types, scopes, rules, PR creation workflow, and full branching workflow examples
tags:
  [
    conventional-commits,
    commit-message,
    semantic-release,
    pr-creation,
    workflow,
  ]
---

# Conventional Commits

## Format

```text
type(scope): subject

body (optional)

footer (optional)
```

## Types

| Type       | Description                               |
| ---------- | ----------------------------------------- |
| `feat`     | New features                              |
| `fix`      | Bug fixes                                 |
| `docs`     | Documentation changes                     |
| `style`    | Code style (formatting, no logic changes) |
| `refactor` | Code changes (neither fix nor feature)    |
| `perf`     | Performance improvements                  |
| `test`     | Adding or correcting tests                |
| `build`    | Build system or external dependencies     |
| `ci`       | CI configuration changes                  |
| `chore`    | Tooling, maintenance, non-src changes     |
| `revert`   | Revert a previous commit                  |

The spec only mandates `feat` and `fix`. The other types are community conventions adopted from the Angular convention and widely used by commitlint.

## Scopes

Scopes vary by project. Common patterns:

| Category | Scopes                             |
| -------- | ---------------------------------- |
| Apps     | `web`, `api`, `mobile`             |
| Packages | `auth`, `config`, `database`, `ui` |
| Tooling  | `deps`, `ci`, `build`              |

Custom scopes are allowed. Scope is optional.

## Rules

- Subject: imperative mood, no period, lowercase
- Header max length: 200 characters
- Body: optional, wrap at 72 characters

## Examples

```bash
# Feature
git commit -m "feat(auth): add password reset flow"

# Bug fix
git commit -m "fix(ui): correct button alignment on mobile"

# Chore
git commit -m "chore(deps): update react to v19"

# With scope
git commit -m "refactor(database): simplify user queries"

# Without scope
git commit -m "docs: update README installation steps"

# Breaking change
git commit -m "feat(api)!: change authentication endpoint response format"
```

## Full Workflow

```bash
# 1. Create branch from main
git checkout main
git pull
git checkout -b feat/my-feature

# 2. Make changes and commit
git add src/
git commit -m "feat(scope): add feature description"

# 3. Push to remote
git push -u origin feat/my-feature

# 4. Create PR
gh pr create --title "feat(scope): add feature description" --body "..."

# 5. After review, merge
gh pr merge --squash
```

## Semantic Versioning Integration

Conventional commits enable automated versioning:

| Commit Type                 | Version Bump  |
| --------------------------- | ------------- |
| `fix`                       | Patch (0.0.x) |
| `feat`                      | Minor (0.x.0) |
| `feat!` / `BREAKING CHANGE` | Major (x.0.0) |

Tools like Semantic Release and Changesets parse commit messages to determine the next version automatically.
