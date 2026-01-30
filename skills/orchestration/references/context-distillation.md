---
title: Context Distillation
description: Symbol indexing, fact extraction, summary chain-of-thought, recursive context reduction, and token management for subagent delegation
tags:
  [
    context-distillation,
    token-management,
    symbol-indexing,
    fact-extraction,
    delegation,
  ]
---

# Context Distillation

Passing the entire project context to every subagent is expensive and leads to "Lost in the Middle" syndrome where the agent ignores crucial information buried in a large context window.

## The Problem

| Approach        | Tokens | Quality | Cost   |
| --------------- | ------ | ------- | ------ |
| Full codebase   | 100k+  | Low     | High   |
| Relevant files  | 10-30k | Medium  | Medium |
| Distilled facts | 1-5k   | High    | Low    |

Distilled context produces better results because the agent focuses on exactly what matters.

## Distillation Techniques

### 1. Symbol Indexing

Instead of passing file contents, pass a list of available functions, classes, and types. The subagent can then request specific file contents only when needed.

```text
Available Symbols:
  - auth/validateSession(token: string): Promise<Session | null>
  - auth/createSession(userId: string): Promise<Session>
  - types/Session { id, userId, expiresAt, createdAt }
  - types/User { id, email, name, role }
```

The subagent sees the shape of the system without reading every file.

### 2. Fact Extraction

Use a context distiller to extract only the facts relevant to the sub-task:

| Original Task                               | Distilled Context                                                                                                                  |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| "Fix the bug in the login flow" (100 files) | "Login uses `auth-expert` via `src/lib/auth.ts`. Error in `validateSession`. Relevant interfaces: `Session`, `User`."              |
| "Add caching to API" (50 files)             | "API uses `ky` client in `src/api/client.ts`. Response types in `src/types/api.ts`. Cache candidates: user list, product catalog." |

### 3. Summary Chain-of-Thought

Before delegating, the parent should write a concise summary:

```text
What we know:
  - Auth system uses JWT tokens stored in cookies
  - Session validation happens in middleware
  - The bug causes 401 errors after token refresh

What we need to find out:
  - Why the refreshed token is not being saved
  - Whether the cookie settings match between set and read
```

## Recursive Context Reduction

As delegation depth increases, the context must become narrower:

| Level | Agent      | Context Scope                       |
| ----- | ---------- | ----------------------------------- |
| 0     | User       | Full problem statement              |
| 1     | Supervisor | Architectural plan + key files      |
| 2     | Worker     | Single function logic + local types |
| 3     | Executor   | Specific tool parameters            |

Each level strips away information not relevant to that level's task. The executor only needs to know about the specific function call, not the entire system architecture.

## Best Practices

| Practice                            | Rationale                                 |
| ----------------------------------- | ----------------------------------------- |
| Pass symbols, not file contents     | Reduces tokens while preserving structure |
| Extract facts relevant to task      | Focuses agent attention on what matters   |
| Write "what we know / need" summary | Prevents objective drift in delegation    |
| Narrow context at each depth        | Deeper agents need less context, not more |
| Allow subagents to request more     | Let them pull specific files when needed  |
| Never pass the entire codebase      | Causes "Lost in the Middle" syndrome      |
