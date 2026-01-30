---
name: tldr-expert
description: 'Performs semantic code intelligence and token optimization through context engineering and automated context packing. Use when reducing token overhead for large codebases, creating repository digests with Gitingest, packaging code context with Repomix, or tracing cross-file dependencies with llm-tldr.'
---

# TLDR Expert

## Overview

Achieves high-fidelity codebase comprehension at a fraction of the token cost through semantic layers, structured digests, and advanced context packaging. Combines Repomix for context packing, Gitingest for repository digests, and llm-tldr for graph-based code analysis.

**When to use:** Reducing prompt overhead for large codebases, onboarding to unfamiliar repositories, mapping cross-file dependencies, creating AI-optimized context bundles.

**When NOT to use:** Small single-file tasks, final implementation debugging (read the full file), real-time code editing.

## Quick Reference

| Pattern            | Tool / Command                                | Key Points                                             |
| ------------------ | --------------------------------------------- | ------------------------------------------------------ |
| Context packing    | `repomix --include "src/**" --compress`       | Package subdirectories into AI-optimized bundles       |
| Signatures only    | `repomix --include "src/**" --no-code-bodies` | Extract function shapes without implementation details |
| Repository digest  | `gitingest . --output digest.txt`             | Prompt-friendly summary for quick onboarding           |
| Dependency graph   | `tldr context src/file.ts --depth 2`          | Recursive type/function retrieval up to N levels       |
| Caller tracing     | `tldr callers functionName`                   | Find every call site to assess change blast radius     |
| Callee tracing     | `tldr callee functionName`                    | Understand what a function depends on internally       |
| Semantic search    | `tldr semantic "session expiration logic"`    | Find logic by meaning when naming is inconsistent      |
| Architecture audit | `tldr arch`                                   | Detect circular deps, layer violations, dead code      |
| Index health check | `tldr status`                                 | Verify index freshness before analysis                 |
| Secret scanning    | Repomix built-in secretlint                   | Ensure context bundles contain no keys or PII          |

## Token Saving Benchmarks

| Method               | Token Usage | Fidelity         | Best For                           |
| -------------------- | ----------- | ---------------- | ---------------------------------- |
| Raw file read        | 100%        | 100%             | Final implementation and debugging |
| Gitingest digest     | 25%         | 85%              | Initial onboarding and planning    |
| Repomix (compressed) | 15%         | 90%              | Context packing for reasoning      |
| llm-tldr query       | 2%          | 95% (structural) | Architectural mapping and tracing  |

## Common Mistakes

| Mistake                                                     | Correct Pattern                                                                    |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Reading entire large files without checking structure first | Run `tldr extract` to get signatures before reading full files                     |
| Using `grep` for dependency tracing across files            | Use `tldr callers`/`callees` tools that understand dynamic imports                 |
| Packing `node_modules` or `dist` into context bundles       | Configure Repomix ignore-list to exclude generated and vendor directories          |
| Assuming semantic search results are exhaustive             | Verify top matches against actual source and cross-reference with `rg`             |
| Running Repomix without compression on large directories    | Use `--compress` or `--signatures-only` flags to stay within context window limits |
| Including irrelevant context that dilutes signal quality    | Follow top-down priority: index, signatures, core logic, then adjacent context     |

## Delegation

- **Repository structure discovery**: Use `Explore` agent to map directory layout and identify key modules before building context bundles
- **Multi-step context packing workflow**: Use `Task` agent to run Gitingest digest, Repomix compression, and llm-tldr indexing in sequence
- **Architecture analysis and planning**: Use `Plan` agent to design context engineering strategy for large monorepos

## References

- [Context Engineering Patterns](references/context-engineering-patterns.md) -- packing strategies, XML tagging, signal-to-noise optimization, warm-up prompts
- [Repomix and Gitingest Mastery](references/repomix-gitingest-mastery.md) -- configuration, signatures-only mode, digest generation, Tree-sitter extraction
- [Semantic Graph Analysis](references/semantic-graph-analysis.md) -- llm-tldr MCP tools, callers/callees, semantic search, architectural audits
