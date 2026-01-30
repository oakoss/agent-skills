---
name: github
description: 'GitHub CLI workflows for repositories, issues, pull requests, actions, releases, and API calls. Use when creating PRs, reviewing code, triaging issues, triggering workflows, publishing releases, or querying the GitHub API.'
---

# GitHub CLI Skill

Use the `gh` CLI to interact with GitHub repositories and services.

## Command Overview

| Area          | Key Commands                                                          |
| ------------- | --------------------------------------------------------------------- |
| Auth          | `gh auth status`, `gh auth login`, `gh auth refresh`                  |
| Repos         | `gh repo clone`, `gh repo create`, `gh repo fork`, `gh repo view`     |
| Issues        | `gh issue list`, `gh issue create`, `gh issue view`, `gh issue close` |
| Pull Requests | `gh pr create`, `gh pr review`, `gh pr merge`, `gh pr checkout`       |
| Actions       | `gh run list`, `gh run view`, `gh workflow run`                       |
| Releases      | `gh release create`, `gh release list`, `gh release upload`           |
| Search        | `gh search repos`, `gh search issues`, `gh search code`               |
| API           | `gh api repos/owner/repo`, `gh api graphql`                           |

## Common Workflows

| Workflow         | Commands                                                                                         |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| Quick PR         | `git checkout -b feat` → commit → push → `gh pr create --fill`                                   |
| Review and merge | `gh pr checkout 45` → review → `gh pr review --approve` → `gh pr merge --squash --delete-branch` |
| Check CI         | `gh pr checks` → `gh run watch`                                                                  |
| Create release   | `gh release create v1.0.0 --generate-notes`                                                      |
| Search code      | `gh search code "function handleAuth" --repo owner/repo`                                         |

## Common Mistakes

| Mistake                                                         | Correct Pattern                                                          |
| --------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Running `gh pr create` without pushing the branch first         | Push with `git push -u origin branch` before creating a PR               |
| Using `gh pr merge` without checking CI status                  | Run `gh pr checks` first or use `gh pr merge --auto` to wait for checks  |
| Forgetting `--fill` when creating PRs from well-written commits | Use `gh pr create --fill` to auto-populate title and body from commits   |
| Using REST API when GraphQL is more efficient for nested data   | Use `gh api graphql` for queries needing related objects in one call     |
| Not authenticating with correct scopes                          | Run `gh auth status` to verify scopes, `gh auth refresh -s scope` to add |

## Delegation

- **Search across repositories for code patterns or issues**: Use `Explore` agent with `gh search code` and `gh search issues`
- **Automate multi-step release workflows**: Use `Task` agent to coordinate branch creation, PR merge, and release publishing
- **Plan repository structure and access controls**: Use `Plan` agent to design team permissions, branch protection, and workflow architecture

## References

- [Repos & Auth](references/repos-auth.md) — Authentication, repository management, configuration, extensions, aliases
- [Issues](references/issues.md) — Issue CRUD, labels, projects, assignments
- [Pull Requests](references/pull-requests.md) — PR creation, review, merge, checkout, checks, diff
- [Actions](references/actions.md) — Workflow runs, manual triggers, secrets, variables
- [Releases & More](references/releases-more.md) — Releases, gists, SSH/GPG keys, search, API
