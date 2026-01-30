---
title: CI Automation
description: GitHub Actions workflow for automated Figma token sync, version checking, and package.json script configuration
tags: [figma, ci, github-actions, automation, sync, version-control]
---

# CI Automation

## GitHub Actions Workflow

```yaml
name: Sync Figma Design Tokens

on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - run: npm install

      - name: Sync design tokens
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_ACCESS_TOKEN }}
        run: npm run sync:design-tokens

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          title: 'chore: sync design tokens from Figma'
          body: 'Automated sync of design tokens from Figma'
          branch: 'figma/sync-tokens'
          commit-message: 'chore: sync design tokens'
```

## Package Scripts

```json
{
  "scripts": {
    "sync:design-tokens": "tsx scripts/sync-design-tokens.ts",
    "export:icons": "tsx scripts/export-icons.ts",
    "generate:icons": "tsx scripts/generate-icon-components.ts",
    "figma:sync-all": "npm run sync:design-tokens && npm run generate:icons"
  }
}
```

## Version Checking

Detect Figma file updates before syncing:

```ts
async function checkForUpdates() {
  const client = new FigmaClient();
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const file = await client.getFile(fileKey);
  const currentVersion = file.version;

  const previousVersion = await getPreviousVersion();

  if (currentVersion !== previousVersion) {
    await syncDesignTokens();
    await savePreviousVersion(currentVersion);
  }
}
```

Store the previous version in a local file or database to avoid unnecessary syncs.
