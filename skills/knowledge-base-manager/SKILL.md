---
name: knowledge-base-manager
description: 'Designs, builds, and maintains knowledge bases bridging document-based (RAG) and entity-based (graph) knowledge systems. Use when selecting KB architecture, curating content for RAG, implementing versioning and governance, or evaluating quality metrics for knowledge systems.'
version: 1.0.0
tags: [knowledge-base, rag, knowledge-graph, curation, versioning, governance]
---

# Knowledge Base Manager

Structured information + quality curation + accessibility. A knowledge base is curated, validated, versioned information designed for questions and reasoning.

## KB Type Selection

| Type                 | Best For                               | Storage                                  | Query Style            |
| -------------------- | -------------------------------------- | ---------------------------------------- | ---------------------- |
| Document-based (RAG) | Docs, FAQs, articles, manuals          | Vector DB (Pinecone, Weaviate, pgvector) | Semantic search        |
| Entity-based (Graph) | Org charts, catalogs, networks         | Graph DB (Neo4j, ArangoDB)               | Relationship traversal |
| Hybrid (RAG + Graph) | Enterprise, medical, legal, e-commerce | Both + linking layer                     | Combined queries       |

## Decision Framework

| Choose         | When                                                                       |
| -------------- | -------------------------------------------------------------------------- |
| Document-based | Mostly unstructured text, preserving full context matters                  |
| Entity-based   | Structured entities with relationships, "how are X and Y related?" queries |
| Hybrid         | Mix of both, complex domains, enterprise knowledge management              |
| No KB needed   | Static docs sufficient, <50 FAQ items, no maintenance resources            |

## 6-Phase Implementation

| Phase         | Goal                                    | Key Actions                                                           |
| ------------- | --------------------------------------- | --------------------------------------------------------------------- |
| 1. Audit      | Understand existing knowledge           | Inventory sources, classify types, choose architecture, define schema |
| 2. Curation   | Transform raw info to quality knowledge | Extract, clean, normalize, deduplicate, add provenance                |
| 3. Storage    | Technical infrastructure                | Deploy database(s), implement search/query, add caching               |
| 4. Quality    | Ensure accuracy and reliability         | Test questions (>90% accuracy), human review, automated checks        |
| 5. Versioning | Track changes over time                 | Snapshot or event-sourced versioning, rollback, audit trail           |
| 6. Governance | Long-term health                        | Maintenance schedule, roles, change process, quality standards        |

## Quality Metrics

| Metric                        | Target   |
| ----------------------------- | -------- |
| Accuracy (test questions)     | >90%     |
| Coverage (questions answered) | >80%     |
| Freshness (avg age)           | <30 days |
| Consistency (no conflicts)    | >95%     |
| Query relevance (user-rated)  | >85%     |
| Query latency (median)        | <100ms   |

## Anti-Patterns

| Anti-Pattern                | Impact                            | Fix                                             |
| --------------------------- | --------------------------------- | ----------------------------------------------- |
| Data dump without curation  | Low signal-to-noise, poor results | Curate before ingesting, quality > quantity     |
| No version control          | Can't audit, can't rollback       | Implement versioning from day 1                 |
| Stale knowledge             | Wrong answers, AI hallucinations  | Freshness monitoring + scheduled updates        |
| Duplicate information       | Conflicting answers               | Deduplication + single source of truth          |
| No provenance               | Can't verify accuracy             | Always track source + timestamp + author        |
| Build it and they will come | Doesn't meet user needs           | Start with user research, validate continuously |
| Perfectionism               | Never launches                    | Launch at 80% coverage, iterate on usage        |
| Over-engineering            | Wasted complexity                 | Start simple, add complexity only when needed   |

## Common Mistakes

| Mistake                                                          | Correct Pattern                                                                       |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Ingesting raw data without curation or normalization             | Curate, clean, and deduplicate before ingesting; quality over quantity                |
| Skipping version control for knowledge base content              | Implement versioning from day one with rollback and audit trail                       |
| Building a KB without validating against user questions          | Start with user research and test against real queries for >90% accuracy              |
| Choosing hybrid architecture when simple document-based suffices | Match architecture to actual query patterns; start simple, add complexity when needed |
| Launching without freshness monitoring or update schedules       | Set up automated freshness checks and scheduled content reviews                       |

## Delegation

- **Audit existing knowledge sources and classify content types**: Use `Explore` agent to inventory documents, assess quality, and identify gaps
- **Implement end-to-end KB pipeline with storage and retrieval**: Use `Task` agent to deploy database, configure search, and run quality checks
- **Design KB architecture and governance model**: Use `Plan` agent to select between document-based, entity-based, or hybrid approaches

## References

- [Architecture and Types](references/architecture.md)
- [Curation and Ingestion](references/curation.md)
- [Storage and Retrieval](references/storage.md)
- [Quality Control](references/quality-control.md)
- [Versioning](references/versioning.md)
- [Governance](references/governance.md)
