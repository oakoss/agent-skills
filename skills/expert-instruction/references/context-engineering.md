---
title: Context Engineering
description: Token optimization techniques, information hierarchy, noise reduction, few-shot anchoring, and structured context packing
tags:
  [
    context-engineering,
    token-optimization,
    few-shot,
    information-hierarchy,
    repomix,
  ]
---

# Context Engineering

## The Information Hierarchy

Not all information is equal. Prioritize context in this order:

1. **Current Request**: The user's immediate goal
2. **Explicit Rules**: Mandatory protocols (skill instructions, CLAUDE.md, project rules)
3. **Active File Content**: The code being modified
4. **Immediate Dependencies**: Interfaces and types used by the active file
5. **Historical Context**: Relevant past commits or similar patterns

## Token Optimization Techniques

- **Symbol Search**: Use grep or rg to find definitions rather than reading entire folders
- **Partial Reads**: Use offset and limit parameters when reading large files
- **Semantic Summarization**: Condense long error logs into a single sentence describing the failure mode and root cause

## Noise Reduction

- **Ignore List**: Strictly exclude `node_modules`, `.next`, `dist`, and binary artifacts from context
- **Redaction**: Remove repetitive boilerplate or large data arrays that do not affect logic
- **Deduplication**: Do not include the same information from multiple sources

## Few-Shot Anchoring

Providing canonical examples is significantly more effective than writing long lists of rules:

- Include one "Gold Standard" implementation for every new pattern
- Place the example close to where the agent will need it
- Use real code from the project rather than synthetic examples when possible

## Structured Context Packing

Use tools like Repomix to bundle related files into a single, structured markdown artifact. This ensures the model understands file boundaries and hierarchical relationships between components.

Key practices:

- Bundle only the files relevant to the current task
- Include type definitions alongside implementation files
- Order files from most general (interfaces, types) to most specific (implementations, tests)
