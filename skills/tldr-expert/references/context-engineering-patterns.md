---
title: Context Engineering Patterns
description: Strategic information packing for LLM context windows including priority hierarchies, XML tagging, signal-to-noise optimization, and warm-up prompts
tags:
  [
    context-engineering,
    token-optimization,
    XML-tagging,
    signal-to-noise,
    packing-strategy,
  ]
---

# Context Engineering Patterns

Context engineering is the practice of selecting, ordering, and formatting information to maximize an LLM's reasoning capability within its context window.

## Top-Down Priority Hierarchy

When packing context for an LLM, follow this priority order. Higher-priority items go first in the context window.

| Priority | Content Type      | Description                                      |
| -------- | ----------------- | ------------------------------------------------ |
| 1        | Project index     | High-level purpose, architecture overview        |
| 2        | Module signatures | Exported functions and types (no implementation) |
| 3        | Core logic        | The specific file being modified (full body)     |
| 4        | Adjacent context  | Related files, documentation, test files         |

**Key principle:** More data is not always better. Irrelevant context leads to "lost in the middle" errors where models fail to attend to important information buried between noise.

## XML Tagging Pattern

Use distinct XML tags to help the model distinguish between different parts of the context. This is the default format used by Repomix.

```xml
<file path="src/auth.ts">
export async function authenticate(token: string): Promise<User> {
  const decoded = verifyJWT(token);
  return findUser(decoded.sub);
}
</file>

<file path="src/types.ts">
export interface User {
  id: string;
  email: string;
  role: 'admin' | 'user';
}
</file>

<instruction_context>
The authentication module uses JWT tokens with RS256 signing.
User roles determine access to admin endpoints.
</instruction_context>
```

## Signal-to-Noise Ratio Optimization

The goal is to increase signal (knowledge) and decrease noise (boilerplate).

### Pruning Imports

Most imports are boilerplate. Remove them from context bundles unless the import source is non-obvious.

```ts
// REMOVE from context (obvious)
import { useState, useEffect } from 'react';
import { z } from 'zod';

// KEEP in context (non-obvious, project-specific)
import { useAuthGuard } from '@/hooks/use-auth-guard';
import { type PaymentIntent } from '@/lib/stripe-types';
```

### Stubbing Constants

If a file has a large constants object, replace it with a stub unless the constants are directly relevant.

```ts
// Original: 500 lines of country codes
export const COUNTRY_CODES = {
  US: 'United States',
  // ... 200+ entries
};

// Stubbed for context: 1 line
export const COUNTRY_CODES: Record<string, string>; // 200+ country code mappings
```

### Type Aggregation

Move all relevant TypeScript interfaces into a single block at the top of the context bundle for quick reference.

## Warm-Up Prompt Pattern

Before asking for a complex change, warm up the model's context by asking it to summarize the provided bundle. This ensures the model has attended to the key parts.

```text
Step 1: Provide Repomix bundle

Step 2: "Read this bundle and list the 3 most critical modules
         for implementing feature X. Explain their roles."

Step 3: "Now, based on that analysis, implement feature X
         following the existing patterns you identified."
```

This two-step approach produces higher-quality output than a single prompt because the model has explicitly processed the relevant modules before generating code.

## Automated Context Packing Protocol

Before tackling a complex feature, prepare a context bundle:

```bash
# Package the relevant subdirectory with compression
repomix --include "src/features/auth/**" --output auth-context.md --compress

# Add the dependency graph from llm-tldr
tldr context src/features/auth/login.ts --depth 2 >> auth-context.md
```

## Troubleshooting

| Issue                        | Likely Cause                    | Corrective Action                                      |
| ---------------------------- | ------------------------------- | ------------------------------------------------------ |
| Model ignores key context    | Important info buried in middle | Move critical content to start or end of context       |
| Output contradicts context   | Conflicting information packed  | Remove contradictory sources; keep authoritative one   |
| Model hallucinates functions | Signatures missing from context | Add module signatures before requesting implementation |
| Token limit exceeded         | Too much implementation detail  | Switch to signatures-only mode with `--no-code-bodies` |
