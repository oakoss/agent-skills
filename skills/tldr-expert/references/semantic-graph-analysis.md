---
title: Semantic Graph Analysis
description: Using llm-tldr MCP tools for graph-based code analysis including callers/callees tracing, semantic search, and architectural audits
tags:
  [
    llm-tldr,
    semantic-search,
    dependency-graph,
    callers,
    callees,
    architecture-audit,
  ]
---

# Semantic Graph Analysis

llm-tldr provides a graph-based view of a project. Instead of seeing files as flat text, it maps relationships between functions, classes, and modules (callers, callees, importers, exporters).

## MCP Tool Reference

### `tldr callers [function_name]`

**Purpose:** Identify the blast radius of a change. If you rename or modify a function, this finds every call site that will be affected.

```bash
# Find all callers of the authenticate function
tldr callers authenticate

# Output:
# src/middleware/auth.ts:15 - verifyRequest()
# src/api/users.ts:32 - getUserProfile()
# src/api/admin.ts:8 - adminGuard()
```

Use this before any refactoring to understand downstream impact.

### `tldr callee [function_name]`

**Purpose:** Understand the implementation dependencies of a function without reading its full body. Lists all internal calls, giving a functional overview.

```bash
# Find what processPayment depends on
tldr callee processPayment

# Output:
# validateCard() - src/lib/validation.ts
# chargeStripe() - src/lib/stripe.ts
# sendReceipt() - src/lib/email.ts
# auditLog() - src/lib/audit.ts
```

### `tldr context [entry_point] --depth N`

**Purpose:** Recursive context retrieval. Finds every type, constant, and utility function required by the entry point up to N levels deep. This is the most token-efficient way to understand a feature.

```bash
# Get full context tree for the login handler, 2 levels deep
tldr context src/features/auth/login.ts --depth 2

# Output includes:
# - Function signatures
# - Type definitions
# - Constants used
# - Utility functions called
# - All resolved up to 2 levels of dependency depth
```

### `tldr arch`

**Purpose:** Detect architectural issues across the codebase.

Detects:

- **Circular dependencies** -- File A imports File B, which imports File A (high technical debt)
- **Layer violations** -- UI layer directly imports DB layer, bypassing the API
- **Dead code** -- Functions or classes with 0 callers and 0 importers

```bash
tldr arch

# Output:
# CIRCULAR: src/auth.ts <-> src/session.ts
# VIOLATION: src/components/Dashboard.tsx -> src/db/queries.ts (UI -> DB)
# DEAD: src/utils/legacy-format.ts:formatV1() - 0 callers
```

### `tldr status`

**Purpose:** Check index health. Run this before any analysis to ensure the index is current.

```bash
tldr status

# Output:
# Index: WARM (last updated 2 min ago)
# Files indexed: 342
# Functions: 1,204
# Types: 456
```

If the index is stale after a significant refactor, run `tldr warm .` to rebuild it.

### `tldr extract [file_path]`

**Purpose:** Extract signatures from a file without reading the full implementation. Use this before reading any file over 500 lines.

```bash
tldr extract src/lib/payment-engine.ts

# Output: exported function and type signatures only
```

## Semantic Search Strategy

When text-based search (`rg`, `grep`) fails because naming is inconsistent, use semantic search to find logic by meaning.

```bash
# Effective semantic queries:
tldr semantic "session expiration and cookie cleanup logic"
tldr semantic "main entry point for the payment gateway"
tldr semantic "JWT token rotation handling"
tldr semantic "components using the bento grid layout"
```

**Tips for effective semantic queries:**

- Describe the behavior, not the function name
- Include domain-specific terms (e.g., "JWT," "bento grid")
- If results are empty, fall back to `rg` for keywords, then use `tldr context` on the results

## Standard Operating Procedure

1. **Check health:** Run `tldr status` to verify index freshness
2. **Map architecture:** Run `tldr arch` to understand layers and detect issues
3. **Discover:** Use semantic search and callers/callees to isolate feature logic
4. **Pack context:** Create a Repomix bundle for the specific sub-module
5. **Execute:** Pass the optimized context to the reasoning model

## Troubleshooting

| Issue                      | Likely Cause                     | Corrective Action                                     |
| -------------------------- | -------------------------------- | ----------------------------------------------------- |
| llm-tldr index stale       | Significant refactor performed   | Run `tldr warm .` to rebuild the index                |
| Semantic search "no match" | Query too specific or index cold | Use `rg` for keywords, then `tldr context` on results |
| Callers returns empty      | Function is unexported or dead   | Check if function is exported; may be dead code       |
| Context depth too large    | Deep dependency chains           | Reduce `--depth` or use `--no-code-bodies` mode       |
