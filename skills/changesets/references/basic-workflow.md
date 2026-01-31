---
title: Basic Workflow
description: Adding changesets, versioning packages, publishing to npm, and integrating with CI pipelines
tags: [add, version, publish, status, changelog, semver, workflow, init]
---

# Basic Workflow

## Initialization

Set up Changesets in a project:

```bash
npx @changesets/cli init
```

This creates a `.changeset/` directory containing:

- `config.json` — configuration options
- `README.md` — instructions for contributors

## Adding a Changeset

When making a change that affects package versions, add a changeset:

```bash
npx @changesets/cli add
```

The interactive prompt asks:

1. Which packages are affected
2. What semver bump type (major, minor, patch)
3. A summary of the change

This creates a markdown file in `.changeset/`:

```markdown
---
'@scope/my-package': minor
'@scope/other-package': patch
---

Add new authentication provider and fix token refresh logic
```

Each changeset file can reference multiple packages with different bump types.

### Empty Changesets

For PRs that do not require version bumps (documentation, CI config, tests):

```bash
npx @changesets/cli add --empty
```

This creates a changeset with no package bumps, satisfying CI status checks.

## Versioning

When ready to release, consume all pending changesets:

```bash
npx @changesets/cli version
```

This command:

- Reads all changeset files in `.changeset/`
- Calculates the final version bump per package (highest bump wins)
- Updates `package.json` version fields
- Updates or creates `CHANGELOG.md` for each affected package
- Bumps internal dependency ranges in dependent packages
- Deletes consumed changeset files

Review the changes, then commit:

```bash
git add .
git commit -m "chore: version packages"
```

## Publishing

After versioning, publish all updated packages to npm:

```bash
npx @changesets/cli publish
```

This command:

- Publishes each package with an updated version
- Creates git tags for each published package (e.g., `@scope/pkg@1.2.0`)
- Skips packages marked as `private: true`

Push tags to remote after publishing:

```bash
git push --follow-tags
```

**Build before publishing.** The `publish` command does not run build scripts. Ensure packages are built before running publish:

```bash
npm run build
npx @changesets/cli publish
```

## Checking Status

View pending changesets and their projected version bumps:

```bash
npx @changesets/cli status
```

Use `--verbose` for detailed per-package breakdown:

```bash
npx @changesets/cli status --verbose
```

The status command exits with code 1 if there are changed packages without changesets. Use this in CI to enforce changeset requirements:

```bash
npx @changesets/cli status --since=main
```

## Changelog Configuration

The default changelog generator is `@changesets/cli/changelog`. For richer changelogs with GitHub links, use `@changesets/changelog-github`:

```bash
npm install -D @changesets/changelog-github
```

Update `.changeset/config.json`:

```json
{
  "changelog": ["@changesets/changelog-github", { "repo": "owner/repo-name" }]
}
```

This adds commit links, PR references, and contributor attribution to changelogs.

## Package.json Scripts

Define convenience scripts for the release workflow:

```json
{
  "scripts": {
    "changeset": "changeset",
    "version-packages": "changeset version",
    "release": "npm run build && changeset publish"
  }
}
```

## Changeset File Format

Each changeset is a markdown file with YAML frontmatter:

```markdown
---
'package-a': major
'package-b': minor
---

Description of the change. This text appears in CHANGELOG.md.

Supports **markdown** formatting for rich changelogs.
```

Valid bump types follow semver:

- **major** — breaking changes (1.x.x -> 2.0.0)
- **minor** — new features, backward compatible (1.1.x -> 1.2.0)
- **patch** — bug fixes, backward compatible (1.1.1 -> 1.1.2)

## Complete Release Workflow

A typical release cycle:

```bash
# 1. Developer adds changeset during feature work
npx @changesets/cli add

# 2. Commit changeset with the PR
git add .changeset/
git commit -m "feat: add new feature"

# 3. When ready to release, consume changesets
npx @changesets/cli version

# 4. Review version bumps and changelogs
git diff

# 5. Commit version changes
git add .
git commit -m "chore: version packages"

# 6. Build and publish
npm run build
npx @changesets/cli publish

# 7. Push commits and tags
git push --follow-tags
```
