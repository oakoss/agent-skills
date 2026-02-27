---
title: CI Automation
description: GitHub Actions workflow for automated Figma token sync, version checking, webhook integration, and package.json script configuration
tags: [figma, ci, github-actions, automation, sync, version-control, webhooks]
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
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: 20

      - run: npm install

      - name: Sync design tokens
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_ACCESS_TOKEN }}
        run: npm run sync:design-tokens

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
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

Detect Figma file updates before syncing to avoid unnecessary work:

```ts
import { Api } from 'figma-api';
import fs from 'fs/promises';

async function checkForUpdates() {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const file = await api.getFile({ file_key: fileKey });
  const currentVersion = file.version;

  let previousVersion: string | null = null;
  try {
    previousVersion = await fs.readFile('.figma-version', 'utf-8');
  } catch {
    // First run
  }

  if (currentVersion !== previousVersion) {
    console.log(`Figma file updated: ${previousVersion} -> ${currentVersion}`);
    await syncDesignTokens();
    await fs.writeFile('.figma-version', currentVersion);
  } else {
    console.log('No updates detected');
  }
}
```

## Webhook-Triggered Sync

Use Figma webhooks for real-time sync instead of polling. Register a webhook for `FILE_UPDATE` events:

```ts
import { Api } from 'figma-api';

async function registerWebhook() {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });

  const webhook = await api.postWebhook({
    event_type: 'FILE_UPDATE',
    team_id: 'YOUR_TEAM_ID',
    endpoint: 'https://your-server.com/api/figma-webhook',
    passcode: process.env.FIGMA_WEBHOOK_PASSCODE!,
  });

  console.log('Webhook registered:', webhook.id);
}
```

Then trigger a GitHub Actions workflow via repository dispatch from your webhook handler.

## Workflow with Version Gate

Combine version checking with the GitHub Actions workflow to skip unnecessary PRs:

```yaml
name: Sync Figma (with version check)

on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    outputs:
      changed: ${{ steps.version.outputs.changed }}
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: 20

      - run: npm install

      - name: Check Figma version
        id: version
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_ACCESS_TOKEN }}
        run: npm run figma:check-version

  sync:
    needs: check
    if: needs.check.outputs.changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: 20

      - run: npm install

      - name: Sync tokens
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_ACCESS_TOKEN }}
        run: npm run figma:sync-all

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          title: 'chore: sync design tokens from Figma'
          branch: 'figma/sync-tokens'
          commit-message: 'chore: sync design tokens'
```
