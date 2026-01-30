---
title: Setup and Authentication
description: Figma API access token setup, environment configuration, FigmaClient initialization, and connection testing
tags: [figma, setup, auth, access-token, environment, client]
---

# Setup and Authentication

## Access Token

1. Go to Figma Settings → Personal access tokens
2. Generate a new token
3. Store in environment:

```bash
FIGMA_ACCESS_TOKEN=figd_...
```

## Client Initialization

```ts
import { FigmaClient } from '@/integrations/design-tools/figma/client';

const client = new FigmaClient({
  accessToken: process.env.FIGMA_ACCESS_TOKEN,
});

const file = await client.getFile('abc123xyz');
```

## Dependencies

```bash
npm install node-fetch
```

For TypeScript types:

```bash
npm install @figma/rest-api-spec
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

Figma supports native variables for colors, spacing, border radius, and typography sizes. Extract these automatically with the API for the most reliable token sync.
