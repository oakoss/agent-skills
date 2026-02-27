---
title: CI Automation
description: GitHub Actions integration, automated version PRs, snapshot releases, and prerelease channels
tags:
  [github-actions, ci, automation, snapshot, prerelease, bot, publish, release]
---

# CI Automation

## GitHub Actions Release Workflow

The official `changesets/action` automates the release process. It operates in two modes:

1. **When changesets exist:** Opens a "Version Packages" PR that consumes all changesets
2. **When the Version Packages PR is merged:** Publishes packages to npm

```yaml
name: Release

on:
  push:
    branches:
      - main

concurrency: ${{ github.workflow }}-${{ github.ref }}

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v6
        with:
          node-version: 20
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build packages
        run: npm run build

      - name: Create Release Pull Request or Publish
        uses: changesets/action@v1
        with:
          version: npm run version-packages
          publish: npm run release
          commit: 'chore: version packages'
          title: 'chore: version packages'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

Required package.json scripts:

```json
{
  "scripts": {
    "version-packages": "changeset version",
    "release": "npm run build && changeset publish"
  }
}
```

### Action Configuration Options

| Option                 | Default              | Description                                  |
| ---------------------- | -------------------- | -------------------------------------------- |
| `version`              | `changeset version`  | Command to run for versioning                |
| `publish`              | `changeset publish`  | Command to run for publishing                |
| `commit`               | `"Version Packages"` | Commit message for version changes           |
| `title`                | `"Version Packages"` | PR title for the version PR                  |
| `setupGitUser`         | `true`               | Configures git user as `github-actions[bot]` |
| `createGithubReleases` | `true`               | Creates GitHub Releases after publish        |
| `commitMode`           | `"git-cli"`          | Use `"github-api"` for GPG-signed commits    |

### pnpm Monorepo Workflow

For pnpm-based monorepos, adjust the workflow:

```yaml
name: Release

on:
  push:
    branches:
      - main

concurrency: ${{ github.workflow }}-${{ github.ref }}

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: Setup pnpm
        uses: pnpm/action-setup@v4

      - name: Setup Node.js
        uses: actions/setup-node@v6
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build packages
        run: pnpm run build

      - name: Create Release Pull Request or Publish
        uses: changesets/action@v1
        with:
          version: pnpm run version-packages
          publish: pnpm run release
          commit: 'chore: version packages'
          title: 'chore: version packages'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Changeset Status Check in CI

Enforce that PRs include changesets for package changes:

```yaml
name: Changeset Check

on:
  pull_request:
    branches:
      - main

jobs:
  changeset-check:
    name: Changeset Check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v6
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Check for changesets
        run: npx @changesets/cli status --since=origin/main
```

Alternatively, install the [Changeset Bot](https://github.com/apps/changeset-bot) GitHub App. It comments on PRs indicating whether a changeset is present, without failing the build.

## Snapshot Releases

Snapshot releases create temporary versions for testing without affecting the main release line. They produce versions like `0.0.0-20240115120000`.

### Manual Snapshot Workflow

```bash
npx @changesets/cli version --snapshot
npx @changesets/cli publish --tag canary --no-git-tag
```

The `--tag canary` flag publishes under a dist-tag other than `latest`, preventing users from accidentally installing snapshot versions.

### Snapshot CI Workflow

Automate snapshot releases on PRs for testing:

```yaml
name: Snapshot Release

on:
  issue_comment:
    types: [created]

jobs:
  snapshot:
    name: Snapshot Release
    if: github.event.comment.body == '/snapshot'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
        with:
          ref: refs/pull/${{ github.event.issue.number }}/head
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v6
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Build packages
        run: npm run build

      - name: Create snapshot versions
        run: npx @changesets/cli version --snapshot pr${{ github.event.issue.number }}

      - name: Publish snapshot
        run: npx @changesets/cli publish --tag pr${{ github.event.issue.number }} --no-git-tag
        env:
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

Install a snapshot release for testing:

```bash
npm install @scope/package@pr123
```

## Prerelease Channels

Prereleases allow publishing beta, alpha, or RC versions before a stable release.

### Entering Prerelease Mode

```bash
npx @changesets/cli pre enter beta
```

This creates a `.changeset/pre.json` file that tracks prerelease state. While in prerelease mode:

- `changeset version` produces versions like `1.0.0-beta.0`, `1.0.0-beta.1`
- Each `version` call increments the prerelease number
- New changesets continue to accumulate

### Prerelease Workflow

```bash
# 1. Enter prerelease mode on a dedicated branch
git checkout -b release/next
npx @changesets/cli pre enter beta

# 2. Version and publish prerelease
npx @changesets/cli version
git add .
git commit -m "chore: version packages (beta)"
npm run build
npx @changesets/cli publish
git push --follow-tags

# 3. Continue adding changesets and versioning
npx @changesets/cli add
npx @changesets/cli version
git add .
git commit -m "chore: version packages (beta)"
npm run build
npx @changesets/cli publish
git push --follow-tags

# 4. Exit prerelease mode for stable release
npx @changesets/cli pre exit
npx @changesets/cli version
git add .
git commit -m "chore: version packages"
npm run build
npx @changesets/cli publish
git push --follow-tags
```

### Prerelease Tags

Common prerelease tags and their conventions:

| Tag     | Use Case                         | Example Version |
| ------- | -------------------------------- | --------------- |
| `alpha` | Early development, unstable      | `2.0.0-alpha.0` |
| `beta`  | Feature complete, testing        | `2.0.0-beta.3`  |
| `rc`    | Release candidate, final testing | `2.0.0-rc.1`    |
| `next`  | Upcoming major version           | `2.0.0-next.5`  |

### Prerelease Branch Strategy

Use a dedicated branch for prereleases to avoid blocking normal releases on `main`:

```text
main (stable releases)
  └── release/next (prerelease channel)
```

The `changesets/action` can be configured to handle prerelease branches by adding the branch to the workflow trigger:

```yaml
on:
  push:
    branches:
      - main
      - 'release/**'
```

## npm Authentication in CI

Configure npm authentication for automated publishing:

```yaml
- name: Create .npmrc
  run: |
    echo "//registry.npmjs.org/:_authToken=${{ secrets.NPM_TOKEN }}" > .npmrc
```

For scoped packages on a private registry:

```yaml
- name: Create .npmrc
  run: |
    echo "@scope:registry=https://npm.pkg.github.com" > .npmrc
    echo "//npm.pkg.github.com/:_authToken=${{ secrets.GITHUB_TOKEN }}" >> .npmrc
```

## Handling Version PR Conflicts

The automated Version Packages PR can develop merge conflicts when multiple PRs with changesets merge in sequence. The `changesets/action` automatically updates the PR on each push to `main`, resolving most conflicts. If manual intervention is needed:

```bash
git checkout changeset-release/main
git merge main
npx @changesets/cli version
git add .
git commit -m "chore: resolve version conflicts"
git push
```
