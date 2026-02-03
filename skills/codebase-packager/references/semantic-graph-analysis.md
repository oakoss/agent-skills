---
title: Semantic Graph Analysis
description: Using llm-tldr CLI tools for graph-based code analysis including impact tracing, semantic search, and architectural audits
tags:
  [
    llm-tldr,
    semantic-search,
    dependency-graph,
    impact-analysis,
    call-graph,
    architecture-audit,
  ]
---

# Semantic Graph Analysis

llm-tldr provides a graph-based view of a project. Instead of seeing files as flat text, it maps relationships between functions, classes, and modules through AST analysis, call graphs, control flow, data flow, and program dependence layers.

## Installation and Setup

llm-tldr is a Python package. Install and initialize:

```bash
pip install llm-tldr
tldr warm .
```

The `warm` command builds all indexes including semantic embeddings. The embedding model (bge-large-en-v1.5, 1.3GB) downloads on first run.

## CLI Command Reference

### `tldr impact <function_name> <project_path>`

**Purpose:** Reverse call graph analysis. Identify the blast radius of a change by finding every call site that would be affected by modifying a function.

```bash
# Find all callers of the authenticate function
tldr impact authenticate .

# Output shows reverse call graph:
# src/middleware/auth.ts:15 - verifyRequest()
# src/api/users.ts:32 - getUserProfile()
# src/api/admin.ts:8 - adminGuard()
```

Use this before any refactoring to understand downstream impact.

### `tldr calls <project_path>`

**Purpose:** Build the forward call graph across the project. Understand what functions call what other functions.

```bash
# Build forward call graph
tldr calls .
```

### `tldr context <function_name> --project <path>`

**Purpose:** Generate an LLM-ready context summary for a function. Extracts the function along with its dependencies, achieving approximately 95% token savings compared to reading entire files.

```bash
# Get LLM-ready context for the login handler
tldr context login --project src/features/auth

# Output includes:
# - Function signatures
# - Type definitions
# - Constants used
# - Utility functions called
```

### `tldr arch <project_path>`

**Purpose:** Detect architectural issues across the codebase.

Detects:

- **Circular dependencies** -- File A imports File B, which imports File A (high technical debt)
- **Layer violations** -- UI layer directly imports DB layer, bypassing the API
- **Dead code** -- Functions or classes with zero callers

```bash
tldr arch .

# Output:
# CIRCULAR: src/auth.ts <-> src/session.ts
# VIOLATION: src/components/Dashboard.tsx -> src/db/queries.ts (UI -> DB)
```

### `tldr dead <project_path>`

**Purpose:** Find unreachable code -- functions with zero callers and zero importers.

```bash
tldr dead .

# Output:
# src/utils/legacy-format.ts:formatV1() - 0 callers
```

### `tldr extract <file_path>`

**Purpose:** Extract the full AST from a file -- functions, classes, and imports -- without reading the full implementation. Use this before reading any file over 500 lines.

```bash
tldr extract src/lib/payment-engine.ts

# Output: exported function and type signatures
```

### `tldr daemon status`

**Purpose:** Check whether the llm-tldr daemon is running. The daemon auto-starts on first query and auto-stops after 5 minutes of inactivity.

```bash
tldr daemon status

# Output:
# Daemon running on port 9119
# Files indexed: 342
```

If the index is stale after a significant refactor, run `tldr warm .` to rebuild it.

### Additional Commands

| Command                           | Purpose                               |
| --------------------------------- | ------------------------------------- |
| `tldr tree <path>`                | Display file structure                |
| `tldr structure <path> --lang ts` | List functions and classes in project |
| `tldr search <pattern> <path>`    | Text pattern search                   |
| `tldr cfg <file> <function>`      | Control flow graph analysis           |
| `tldr dfg <file> <function>`      | Data flow graph analysis              |
| `tldr slice <file> <func> <line>` | Program dependence slicing            |
| `tldr imports <file>`             | Parse imports from a file             |
| `tldr importers <module> <path>`  | Find files that import a module       |
| `tldr diagnostics <file>`         | Type check and lint a file            |
| `tldr change-impact <files>`      | Find tests affected by file changes   |
| `tldr daemon start`               | Start background daemon               |
| `tldr daemon stop`                | Stop background daemon                |

## Semantic Search Strategy

When text-based search (`rg`, `grep`) fails because naming is inconsistent, use semantic search to find logic by meaning.

```bash
# Effective semantic queries:
tldr semantic "session expiration and cookie cleanup logic" .
tldr semantic "main entry point for the payment gateway" .
tldr semantic "JWT token rotation handling" .
tldr semantic "components using the bento grid layout" .
```

**Tips for effective semantic queries:**

- Describe the behavior, not the function name
- Include domain-specific terms (e.g., "JWT," "bento grid")
- If results are empty, fall back to `rg` for keywords, then use `tldr context` on the results
- The semantic index is cached in `.tldr/cache/semantic.faiss`

## MCP Server Integration

llm-tldr can operate as an MCP server for Claude Code and Claude Desktop:

```json
{
  "mcpServers": {
    "tldr": {
      "command": "tldr-mcp",
      "args": ["--project", "/path/to/project"]
    }
  }
}
```

## Standard Operating Procedure

1. **Build indexes:** Run `tldr warm .` to build all indexes including embeddings
2. **Map architecture:** Run `tldr arch .` to understand layers and detect issues
3. **Discover:** Use semantic search and impact analysis to isolate feature logic
4. **Pack context:** Create a Repomix bundle for the specific sub-module
5. **Execute:** Pass the optimized context to the reasoning model

## Troubleshooting

| Issue                      | Likely Cause                      | Corrective Action                                     |
| -------------------------- | --------------------------------- | ----------------------------------------------------- |
| llm-tldr index stale       | Significant refactor performed    | Run `tldr warm .` to rebuild the index                |
| Semantic search "no match" | Query too specific or index cold  | Use `rg` for keywords, then `tldr context` on results |
| Impact returns empty       | Function is unexported or dead    | Check if function is exported; may be dead code       |
| Daemon not responding      | Daemon timed out after inactivity | Run `tldr daemon start` or any query to auto-start    |
