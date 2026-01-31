---
title: Setup and Authentication
description: Figma API access token setup, environment configuration, figma-api client initialization, and connection testing
tags: [figma, setup, auth, access-token, environment, client]
---

# Setup and Authentication

## Access Token

1. Go to Figma Settings -> Personal access tokens
2. Generate a new token with appropriate scopes (`file_content:read` for most use cases)
3. Store in environment:

```bash
FIGMA_ACCESS_TOKEN=figd_...
```

## Client Initialization with figma-api

The `figma-api` package provides a typed client wrapping the Figma REST API:

```ts
import { Api } from 'figma-api';

const api = new Api({
  personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
});

const file = await api.getFile({ file_key: 'abc123xyz' });
console.log('Connected! File:', file.name);
```

## Direct REST API Usage

For projects that prefer no dependencies, call the REST API directly:

```ts
const FIGMA_BASE = 'https://api.figma.com/v1';

async function figmaGet(path: string) {
  const res = await fetch(`${FIGMA_BASE}${path}`, {
    headers: {
      'X-Figma-Token': process.env.FIGMA_ACCESS_TOKEN!,
    },
  });

  if (!res.ok) {
    throw new Error(`Figma API ${res.status}: ${await res.text()}`);
  }

  return res.json();
}

const file = await figmaGet('/files/YOUR_FILE_KEY');
```

## Dependencies

```bash
npm install figma-api
```

For TypeScript types only (no runtime client):

```bash
npm install --save-dev @figma/rest-api-spec
```

Type usage:

```ts
import { type GetFileResponse } from '@figma/rest-api-spec';
```

## Figma File Organization

Structure Figma files for automated extraction:

```sh
Design System File
├── Cover (description)
├── Colors (all color styles)
├── Typography (all text styles)
├── Spacing (spacing guide)
├── Components
│   ├── Buttons
│   ├── Forms
│   └── Cards
└── Icons (all icons in one frame)
```

## Naming Conventions

Use `/` hierarchy for automated parsing:

```text
Colors:      Primary/500, Secondary/500, Neutral/100
Typography:  Heading/Large, Body/Regular, Body/Small
Components:  Button/Primary, Button/Secondary, Card/Default
```

## Figma Variables

Figma supports native variables for colors, spacing, border radius, and typography sizes. Extract these via the Variables API endpoints:

```ts
const localVars = await api.getLocalVariables({ file_key: 'YOUR_FILE_KEY' });
const publishedVars = await api.getPublishedVariables({
  file_key: 'YOUR_FILE_KEY',
});
```
