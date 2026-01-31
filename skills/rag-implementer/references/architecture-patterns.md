---
title: Architecture Patterns and Prerequisites
description: RAG architecture tiers, prerequisites validation, cost analysis, and decision tree for when to build RAG
tags: [architecture, prerequisites, cost, decision-tree, validation]
---

# Architecture Patterns and Prerequisites

## Prerequisites: Validate the Need for RAG

**Before implementing RAG, confirm:**

- Problem validated with users
- Users need AI search (tested with simpler alternatives)
- ROI justified (cost vs benefit calculated)

### Try These FIRST (Before RAG)

**1. FAQ Page / Documentation (1 day, $0)**

- Create well-organized FAQ or docs
- Add search with Cmd+F
- Works for: <50 common questions, static content

**2. Simple Keyword Search (2-3 days, $0-20/month)**

- Use Algolia, Typesense, or PostgreSQL full-text search
- Good enough for 80% of use cases
- Works for: <100k documents, keyword matching sufficient

**3. Manual Curation / Concierge MVP (1 week, $0)**

- Manually answer user questions
- Build FAQ from common questions
- Works for: <100 users, validating if users want AI

**4. Simple Semantic Search (1 week, $30-50/month)**

- Use OpenAI embeddings + Postgres pgvector
- Skip complex retrieval, re-ranking, etc.
- Works for: <50k documents, basic semantic search

### Decision Tree

```text
Do users need to search your content?
|
+- No -> Don't build RAG
|
+- Yes
   +- <50 items? -> FAQ page ($0)
   |
   +- >50 items?
      +- Keyword search enough? -> Use Algolia ($0-20/mo)
      |
      +- Need semantic understanding?
         +- <50k docs? -> Simple semantic search via pgvector ($30/mo)
         |
         +- >50k docs?
            +- Validated with users? -> Build RAG
            +- Not validated? -> Test with Concierge MVP first
```

## Architecture Tiers

### Naive RAG (Prototype)

- Time: 1-2 weeks
- Cost: $50-150/month
- Scale: <10k documents
- Components: Basic embedding + vector store + simple retrieval

### Advanced RAG (Production)

- Time: 3-4 weeks
- Cost: $200-500/month
- Scale: 10k-1M documents
- Components: Hybrid search, re-ranking, monitoring

### Modular RAG (Enterprise)

- Time: 6-8 weeks
- Cost: $500-2000+/month
- Scale: 1M+ documents
- Components: Multiple knowledge bases, specialized modules

## Modular RAG Architecture

- **Search Module**: Query understanding, reformulation, and hybrid retrieval
- **Memory Module**: Long-term conversation persistence and context accumulation
- **Routing Module**: Query routing to specialized knowledge bases or retrieval strategies
- **Predict Module**: Anticipatory pre-loading based on context
- **Graph Module**: Knowledge graph traversal for multi-hop reasoning (GraphRAG)

## Hybrid RAG + Fine-tuning

- RAG for dynamic, frequently changing knowledge
- Fine-tuning for domain-specific reasoning patterns
- Combine strengths for maximum effectiveness

## GraphRAG

- Build knowledge graphs by extracting entities and relationships from documents
- Enable multi-hop reasoning: "What projects did employees in department X work on?"
- Combine graph traversal with vector similarity for structured + unstructured queries
- Best suited for datasets with rich entity relationships (org charts, product catalogs, research papers)

## Key RAG Principles

1. **Relevance Over Volume** -- Quality curation over massive datasets; remove outdated content continuously
2. **Semantic Understanding** -- Use embeddings for true semantic matching, recognize query intent
3. **Multi-Modal Intelligence** -- Handle text, images, code, tables; enable cross-modal retrieval
4. **Temporal Awareness** -- Prioritize recent info for time-sensitive topics
5. **Transparency and Trust** -- Always provide source citations and confidence levels
