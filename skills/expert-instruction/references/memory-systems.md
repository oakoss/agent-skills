---
title: Memory Systems
description: Tiered memory architecture including short-term context, mid-term working memory, long-term experience, memory gates, and shared team memory
tags:
  [
    memory,
    context-window,
    working-memory,
    long-term,
    vector-database,
    shared-memory,
  ]
---

# Memory Systems

## Short-Term Memory (Context Window)

- **Focus**: Current session history and immediate task details
- **Limit**: Varies by model (200k to 2M tokens)
- **Management**: Handled by context engineering to keep relevant information prioritized

The context window is the most constrained resource. Every token spent on irrelevant history is a token unavailable for reasoning about the current task.

## Mid-Term Memory (Working Context)

- **Focus**: Active project files, recently visited documentation, and in-flight feature specs
- **Implementation**: A persistent knowledge graph or vector index of the current repository

Working memory bridges the gap between immediate session context and long-term patterns. It stores facts about the current project that persist across sessions but are too volatile for permanent storage.

## Long-Term Memory (Experience Repository)

- **Focus**: Historical patterns, past bugs, user preferences, and architectural lessons learned
- **Mechanism**:
  1. **Extraction**: Summarizing key learnings after each completed task
  2. **Embedding**: Storing in a vector database (Pinecone, Supabase Vector, or equivalent)
  3. **Retrieval**: Automatic querying based on current task similarity

Long-term memory allows agents to avoid repeating mistakes and apply proven patterns from previous work.

## The Memory Gate

Agents must not store sensitive data (keys, PII, credentials) in any memory tier.

- Run a secret scrub before persisting any memory vector
- Filter out environment variables, API tokens, and personal identifiable information
- Audit stored memories periodically for accidentally persisted secrets

## Shared Memory (Team Knowledge)

Across a team, agents can share common project knowledge:

- Use `project.json` or `memory.json` in the project root to store collaborative facts
- Shared memory includes framework versions, architectural decisions, team conventions, and known issues
- Keep shared memory concise and actively pruned to prevent context pollution
