---
title: Publishing
description: Automated package publishing, version management, branch configurations, and conventional commit versioning
tags:
  [
    publish,
    versioning,
    conventional-commits,
    npm,
    github-releases,
    branchConfigs,
    monorepo,
  ]
---

# Publishing

## Installation

```bash
pnpm add -D @tanstack/publish-config
```

## Basic Publish Script

Create a publish script that uses the `publish` function from `@tanstack/publish-config`:

```ts
// scripts/publish.ts
import { publish } from '@tanstack/publish-config';

publish({
  branchConfigs: {
    main: {
      prerelease: false,
    },
    beta: {
      prerelease: true,
    },
    alpha: {
      prerelease: true,
    },
  },
  packages: [
    {
      name: '@tanstack/my-core',
      packageDir: 'packages/core',
    },
    {
      name: '@tanstack/my-react',
      packageDir: 'packages/react',
    },
  ],
  rootDir: process.cwd(),
  branch: process.env.BRANCH,
  tag: process.env.TAG,
  ghToken: process.env.GH_TOKEN,
})
  .then(() => {
    console.log('Successfully published packages!');
  })
  .catch((error) => {
    console.error('Publishing failed:', error);
    process.exit(1);
  });
```

The `publish` function is only available as an ESM import. Ensure your project has `"type": "module"` in `package.json`.

## Publish Options

| Option          | Type                           | Description                                 |
| --------------- | ------------------------------ | ------------------------------------------- |
| `branchConfigs` | `Record<string, BranchConfig>` | Maps branch names to release configurations |
| `packages`      | `Array<{ name, packageDir }>`  | List of packages to publish                 |
| `rootDir`       | `string`                       | Root directory of the monorepo              |
| `branch`        | `string` (optional)            | Override current branch detection           |
| `tag`           | `string` (optional)            | Manual version tag, must start with `v`     |
| `ghToken`       | `string` (optional)            | GitHub token for user lookups and releases  |

## Branch Configurations

Branch configs control how each branch publishes to npm:

```ts
const branchConfigs = {
  // Stable releases, tagged as 'latest' on npm
  main: {
    prerelease: false,
  },

  // Beta prereleases, tagged as 'beta' on npm
  beta: {
    prerelease: true,
  },

  // Alpha prereleases, tagged as 'alpha' on npm
  alpha: {
    prerelease: true,
  },

  // Previous major version, tagged as 'previous' on npm
  v4: {
    prerelease: false,
    previousVersion: true,
  },
};
```

Each branch maps to an npm dist-tag:

- `main` with `prerelease: false` publishes as `latest`
- `beta` with `prerelease: true` publishes as `beta`
- `alpha` with `prerelease: true` publishes as `alpha`
- Branches with `previousVersion: true` publish as `previous`

## Conventional Commit Versioning

The publish system determines version bumps from conventional commit messages:

| Commit Type       | Release Level | Example                              |
| ----------------- | ------------- | ------------------------------------ |
| `fix`             | Patch (0.0.x) | `fix: resolve race condition`        |
| `refactor`        | Patch (0.0.x) | `refactor: simplify internal logic`  |
| `perf`            | Patch (0.0.x) | `perf: optimize query deduplication` |
| `feat`            | Minor (0.x.0) | `feat: add new query option`         |
| `BREAKING CHANGE` | Major (x.0.0) | Requires manual `TAG=vX.0.0`         |

Breaking changes indicated by `BREAKING CHANGE` in the commit body or `feat!:` prefix require a manual tag for major version bumps.

## Manual Version Tags

For major version bumps or specific version overrides, pass a tag via environment variable:

```bash
TAG=v2.0.0 BRANCH=main npx tsx scripts/publish.ts
```

The tag must start with `v` followed by a valid semver version.

## Monorepo Package Configuration

Define each publishable package with its name and directory:

```ts
const packages = [
  {
    name: '@tanstack/config',
    packageDir: 'packages/config',
  },
  {
    name: '@tanstack/vite-config',
    packageDir: 'packages/vite-config',
  },
  {
    name: '@tanstack/publish-config',
    packageDir: 'packages/publish-config',
  },
  {
    name: '@tanstack/eslint-config',
    packageDir: 'packages/eslint-config',
  },
];
```

## GitHub Actions Integration

A typical CI workflow for publishing:

```yaml
name: Publish
on:
  push:
    branches: [main, beta, alpha]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          registry-url: 'https://registry.npmjs.org'
      - run: pnpm install
      - run: pnpm build
      - run: npx tsx scripts/publish.ts
        env:
          BRANCH: ${{ github.ref_name }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Requirements

The following tools must be available in the publishing environment:

- **Node.js v18.17+**
- **pnpm v8+** (only supported package manager)
- **Git CLI** (for commit history analysis)
- **GitHub CLI** (pre-installed on GitHub Actions)
