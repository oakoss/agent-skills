---
title: Secure Server Actions
description: Hardening Next.js server actions for AI integrations including server-only patterns, Zod validation, rate limiting, secret management, and stream security
tags:
  [
    server-actions,
    input-validation,
    rate-limiting,
    zod,
    streaming-security,
    secret-management,
  ]
---

# Secure Server Actions

Next.js server actions are the secure bridge between the frontend and AI backend. Every action that interacts with an LLM must enforce authentication, validation, rate limiting, and output filtering.

## Server-Only Pattern

AI logic and API keys must never leak to the client bundle. Use the `server-only` import to enforce this at build time.

```ts
import 'server-only';
import { auth } from '@/auth';
import { z } from 'zod';

const TaskSchema = z.object({
  prompt: z.string().min(1).max(500),
  contextId: z.string().uuid(),
});

export async function processAiTask(formData: FormData) {
  const session = await auth();
  if (!session) throw new Error('Unauthorized');

  const validated = TaskSchema.parse(Object.fromEntries(formData));

  const result = await callAiService({
    prompt: validated.prompt,
    contextId: validated.contextId,
    userId: session.user.id,
  });

  return result;
}
```

## Input Validation with Zod

Never pass raw user input directly to an AI service. Define strict schemas for every server action.

```ts
import { z } from 'zod';

const ChatInputSchema = z.object({
  message: z.string().min(1).max(2000).trim(),
  conversationId: z.string().uuid(),
  model: z.enum(['gpt-4o', 'claude-sonnet']).default('gpt-4o'),
});

const FeedbackSchema = z.object({
  responseId: z.string().uuid(),
  rating: z.number().int().min(1).max(5),
  comment: z.string().max(500).optional(),
});
```

**Validation rules for AI inputs:**

- Maximum length limits on all string fields
- Enum constraints for model selection and mode parameters
- UUID validation for all identifier fields
- Trim whitespace to prevent boundary-marker injection
- Reject inputs containing known injection patterns

## Rate Limiting

AI tokens are expensive. Prevent denial-of-wallet attacks by rate limiting server actions per user and per IP.

```ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '1 m'),
  prefix: 'ai-action',
});

export async function rateLimitedAiAction(formData: FormData) {
  const session = await auth();
  if (!session) throw new Error('Unauthorized');

  const { success, remaining } = await ratelimit.limit(session.user.id);
  if (!success) {
    throw new Error(
      `Rate limit exceeded. Try again in 1 minute. Remaining: ${remaining}`,
    );
  }

  return processAiTask(formData);
}
```

**Rate limit tiers:**

| Tier       | Requests/min | Token budget/hr | Use case               |
| ---------- | ------------ | --------------- | ---------------------- |
| Free       | 5            | 10,000          | Basic chat             |
| Pro        | 30           | 100,000         | Power users            |
| Enterprise | 100          | 1,000,000       | Automated pipelines    |
| Agent      | 50           | 500,000         | Autonomous agent tasks |

## Secret Management

- Use `process.env` for all API keys and secrets
- Never hardcode keys in source files
- Run `gitleaks` in CI to detect committed secrets
- Rotate keys on a regular schedule
- Use different keys for development, staging, and production

```bash
# CI pipeline secret scanning
gitleaks detect --source . --report-format json --report-path gitleaks-report.json
```

## Streaming Security

When streaming AI responses to the frontend, apply server-side filtering to prevent leaking sensitive information.

```ts
import { type NextRequest } from 'next/server';

const SENSITIVE_PATTERNS = [
  /sk-[a-zA-Z0-9]{48}/g,
  /\b\d{3}-\d{2}-\d{4}\b/g,
  /internal-id:[a-f0-9-]+/g,
];

function scrubStream(chunk: string): string {
  let scrubbed = chunk;
  for (const pattern of SENSITIVE_PATTERNS) {
    scrubbed = scrubbed.replace(pattern, '[REDACTED]');
  }
  return scrubbed;
}

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session) return new Response('Unauthorized', { status: 401 });

  const aiStream = await getAiStream(request);

  const scrubbedStream = new TransformStream({
    transform(chunk, controller) {
      controller.enqueue(scrubStream(new TextDecoder().decode(chunk)));
    },
  });

  return new Response(aiStream.pipeThrough(scrubbedStream));
}
```

## Server Action Security Checklist

| Check                           | Required |
| ------------------------------- | -------- |
| `server-only` import            | Yes      |
| Authentication verification     | Yes      |
| Zod input validation            | Yes      |
| Rate limiting                   | Yes      |
| Output scrubbing (if streaming) | Yes      |
| Audit logging                   | Yes      |
| Error sanitization              | Yes      |
| CSRF protection                 | Built-in |
