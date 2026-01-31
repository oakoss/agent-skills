---
title: Build and Publish
description: Build scripts, prepublishOnly, npm pack verification, provenance attestation, scoped packages, and access control
tags:
  [
    prepublishOnly,
    npm-pack,
    provenance,
    scoped-packages,
    npm-publish,
    trusted-publishers,
    access,
  ]
---

# Build and Publish

## Lifecycle Scripts

npm runs scripts in a specific order during `npm publish`:

```text
prepublishOnly -> prepare -> prepack -> postpack -> publish -> postpublish
```

### `prepublishOnly`

Runs only on `npm publish`, not on `npm install`. Use it to ensure the build is fresh:

```json
{
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "prepublishOnly": "npm run build"
  }
}
```

### `prepare`

Runs on both `npm install` (for git dependencies) and `npm publish`. Useful for packages installed directly from git:

```json
{
  "scripts": {
    "prepare": "npm run build"
  }
}
```

## Verifying Package Contents

### `npm pack --dry-run`

Preview exactly what will be published without creating the tarball:

```bash
npm pack --dry-run
```

Output shows every file, its size, and the total package size. Check for:

- No `src/`, `node_modules/`, test files, or config files leaking in
- All `dist/` files present (JS, type declarations, source maps if desired)
- Package size is reasonable

### `npm pack`

Create the actual tarball for local inspection:

```bash
npm pack
```

This creates a `.tgz` file. Extract and inspect it, or install it in a test project:

```bash
mkdir /tmp/test-install && cd /tmp/test-install
npm init -y
npm install /path/to/my-lib-1.0.0.tgz
```

### `publint`

Use `publint` to catch common package.json configuration issues:

```bash
npx publint
```

### `attw` (Are the Types Wrong?)

Verify type declarations resolve correctly across all TypeScript module resolution modes:

```bash
npx @arethetypeswrong/cli --pack .
```

This checks `node10`, `node16` (CJS), `node16` (ESM), and `bundler` resolution modes.

## Provenance

Provenance provides cryptographic proof of where and how a package was built, linking the published package to its source repository and CI build.

### GitHub Actions with Trusted Publishers

The recommended approach uses npm trusted publishing (no long-lived tokens):

```yaml
name: Publish
on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: https://registry.npmjs.org
      - run: npm ci
      - run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

Key requirements:

- `id-token: write` permission is mandatory for provenance
- Trusted publishers eliminate the need for `NPM_TOKEN` (configure on npmjs.com under package settings)
- Provenance is not supported for private repositories publishing public packages
- Only works on cloud-hosted CI runners

### Manual Publishing with Provenance

For local publishing (not recommended for production):

```bash
npm publish --provenance
```

This requires the npm CLI to be able to generate an OIDC token, which only works in supported CI environments.

## Scoped Packages

### First Publish

Scoped packages (`@org/package`) are private by default. To publish publicly:

```bash
npm publish --access public
```

Or set it permanently in `package.json`:

```json
{
  "name": "@my-org/my-lib",
  "publishConfig": {
    "access": "public"
  }
}
```

### `publishConfig`

Override registry or access settings for publishing:

```json
{
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org"
  }
}
```

This is useful for monorepos where the root `.npmrc` might point to a different registry.

## Version Management

### Manual Versioning

```bash
npm version patch -m "release: %s"
npm version minor -m "release: %s"
npm version major -m "release: %s"
```

This updates `package.json`, creates a git commit, and tags it.

### Changesets (Monorepo-Friendly)

For multi-package repos, `changesets` manages versioning and changelogs:

```bash
npx changeset
npx changeset version
npx changeset publish
```

## Pre-Publish Checklist

1. **Version bumped** in `package.json`
2. **Build passes** with latest source
3. **`npm pack --dry-run`** shows correct files and reasonable size
4. **`npx publint`** reports no issues
5. **`npx @arethetypeswrong/cli --pack .`** shows no type resolution problems
6. **Tests pass** against the built output, not source
7. **`README.md`** is current (displayed on npmjs.com)
8. **`LICENSE`** file present
9. **No secrets** in published files (check `.env`, credentials)
10. **Provenance** enabled in CI pipeline
