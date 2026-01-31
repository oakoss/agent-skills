---
title: Monorepo Setup
description: Monorepo configuration, linked packages, fixed versioning, ignore patterns, and internal dependencies
tags:
  [
    monorepo,
    config,
    linked,
    fixed,
    ignore,
    access,
    internal-dependencies,
    baseBranch,
  ]
---

# Monorepo Setup

## Configuration File

All Changesets configuration lives in `.changeset/config.json`. The full default configuration:

```json
{
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "fixed": [],
  "linked": [],
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": []
}
```

## Configuration Options

### `changelog`

Controls changelog generation. Can be a string (package name) or a tuple with options:

```json
{
  "changelog": "@changesets/cli/changelog"
}
```

With GitHub integration for PR links and author attribution:

```json
{
  "changelog": ["@changesets/changelog-github", { "repo": "owner/repo-name" }]
}
```

Set to `false` to disable changelog generation entirely:

```json
{
  "changelog": false
}
```

### `commit`

When `true`, `changeset version` and `changeset add` automatically create git commits:

```json
{
  "commit": true
}
```

### `access`

Controls npm publish access. Set to `"public"` for public scoped packages:

```json
{
  "access": "public"
}
```

Use `"restricted"` (default) for private registry or scoped private packages.

### `baseBranch`

The branch that Changesets compares against for detecting changes:

```json
{
  "baseBranch": "main"
}
```

### `updateInternalDependencies`

Controls how internal dependency ranges are updated when a dependency is bumped:

```json
{
  "updateInternalDependencies": "patch"
}
```

- `"patch"` (default) — always update the dependency range
- `"minor"` — only update when the bump is minor or major

## Linked Packages

Linked packages always share the **highest bump type** within a release. If one package gets a major bump, all linked packages get a major bump. Each package may have a different version number.

Explicit package list:

```json
{
  "linked": [["@scope/components", "@scope/theme", "@scope/tokens"]]
}
```

Using glob patterns (micromatch format, matches against package names):

```json
{
  "linked": [["@scope/ui-*"]]
}
```

Multiple independent link groups:

```json
{
  "linked": [["@scope/react-*"], ["@scope/vue-*"]]
}
```

### How Linked Packages Work

Given packages A (1.0.0) and B (1.0.0) in the same linked group:

- A changeset bumps A as `minor` and B as `patch`
- Both get a `minor` bump (highest wins)
- A becomes 1.1.0, B becomes 1.1.0

Linked packages share bump magnitude but **not** version numbers. Use `fixed` if packages must have identical versions.

## Fixed Packages

Fixed packages always share the **exact same version**. When any package in the group is bumped, all packages get the same version.

```json
{
  "fixed": [["@scope/core", "@scope/react", "@scope/vue"]]
}
```

Using glob patterns:

```json
{
  "fixed": [["@scope/sdk-*"]]
}
```

### How Fixed Packages Work

Given packages A (1.0.0) and B (1.0.0) in the same fixed group:

- A changeset bumps only A as `minor`
- Both A and B become 1.1.0
- All packages in the group always have the same version

Dependencies between packages in a fixed group are **not** considered for additional version bumping since they always move together.

### Linked vs Fixed Comparison

| Behavior       | Linked                                     | Fixed                                |
| -------------- | ------------------------------------------ | ------------------------------------ |
| Bump type      | Shared (highest wins)                      | Shared (highest wins)                |
| Version number | Independent per package                    | Identical across group               |
| Use case       | Related packages that evolve independently | Packages that must always be in sync |
| Example        | Design system components                   | SDK core + framework bindings        |

## Ignore Patterns

Exclude packages from Changesets versioning entirely:

```json
{
  "ignore": ["@scope/internal-tool", "@scope/dev-scripts"]
}
```

Using glob patterns:

```json
{
  "ignore": ["@scope/internal-*"]
}
```

**Restrictions on ignore:**

- Cannot ignore a package that is depended on by a non-ignored package
- Ignored packages skip version bumps entirely, including internal dependency updates
- Use sparingly — ignored packages with dependents can leave the repo in a broken state

## Monorepo Directory Structure

A typical monorepo layout with Changesets:

```sh
monorepo/
├── .changeset/
│   ├── config.json
│   └── README.md
├── packages/
│   ├── core/
│   │   ├── package.json
│   │   ├── CHANGELOG.md
│   │   └── src/
│   ├── react/
│   │   ├── package.json
│   │   ├── CHANGELOG.md
│   │   └── src/
│   └── utils/
│       ├── package.json
│       ├── CHANGELOG.md
│       └── src/
└── package.json
```

Each package gets its own `CHANGELOG.md`, generated and maintained by `changeset version`.

## Internal Dependencies

When a package is bumped, Changesets automatically updates dependent packages within the monorepo.

Given this dependency graph:

```text
@scope/react depends on @scope/core
@scope/vue depends on @scope/core
```

A `minor` bump to `@scope/core` triggers:

- `@scope/core` version bump (minor)
- `@scope/react` dependency range update (patch bump by default)
- `@scope/vue` dependency range update (patch bump by default)

Control this behavior with `updateInternalDependencies`:

```json
{
  "updateInternalDependencies": "minor"
}
```

With `"minor"`, dependents only get bumped if the dependency bump is minor or higher. Patch bumps to dependencies do not cascade.

## Public Monorepo Configuration Example

A complete config for a public monorepo with GitHub changelogs:

```json
{
  "changelog": ["@changesets/changelog-github", { "repo": "owner/repo-name" }],
  "commit": false,
  "fixed": [],
  "linked": [["@scope/react-*"]],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": ["@scope/internal-docs"]
}
```
