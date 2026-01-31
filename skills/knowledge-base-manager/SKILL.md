---
name: knowledge-base-manager
description: 'Designs, builds, and maintains knowledge bases bridging document-based (RAG) and entity-based (graph) knowledge systems. Use when selecting KB architecture, curating content for RAG, implementing versioning and governance, or evaluating quality metrics for knowledge systems.'
license: MIT
metadata:
  author: oakoss
  version: '1.0'
---

# Knowledge Base Manager

## Overview

Provides a structured methodology for designing, building, and maintaining knowledge bases that serve as curated, validated, and versioned information stores for questions and reasoning. Use when building AI-grounded information systems, unifying multiple knowledge sources, or establishing governance for organizational knowledge. Not needed when static documentation suffices, fewer than 50 FAQ items cover all questions, or no maintenance resources are available.

## Quick Reference

| Aspect                 | Options                                            | Key Considerations                                                 |
| ---------------------- | -------------------------------------------------- | ------------------------------------------------------------------ |
| **Architecture**       | Document-based (RAG), Entity-based (Graph), Hybrid | Match to query patterns; start simple, add complexity when needed  |
| **Document-based**     | Vector DB (Pinecone, Weaviate, pgvector)           | Best for docs, FAQs, manuals; semantic search; easy to add content |
| **Entity-based**       | Graph DB (Neo4j, ArangoDB)                         | Best for org charts, catalogs, networks; relationship traversal    |
| **Hybrid**             | Both + linking layer                               | Enterprise, medical, legal; combined queries; highest complexity   |
| **When to skip KB**    | Static docs, <50 FAQ items                         | No maintenance resources, information never changes                |
| **Implementation**     | 6 phases                                           | Audit, Curation, Storage, Quality, Versioning, Governance          |
| **Accuracy target**    | >90% on test questions                             | Create 100+ test questions with known correct answers              |
| **Coverage target**    | >80% questions answerable                          | Validate against real user queries continuously                    |
| **Freshness target**   | <30 days average age                               | Automated freshness monitoring + scheduled updates                 |
| **Consistency target** | >95% conflict-free                                 | Deduplication + single source of truth                             |
| **Query latency**      | <100ms median                                      | Caching and optimization for common access patterns                |
| **Versioning**         | Snapshot, Event-sourced, Git-style                 | Snapshot for simple; event-sourced for audit; git-style for teams  |
| **Maintenance**        | Daily, Weekly, Monthly, Quarterly                  | Establish schedule from day 1; monitor errors and user feedback    |

## Common Mistakes

| Mistake                                                    | Correct Pattern                                                                        |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Ingesting raw data without curation or normalization       | Curate, clean, and deduplicate before ingesting; quality over quantity                 |
| Skipping version control for KB content                    | Implement versioning from day one with rollback and audit trail                        |
| Building a KB without validating against user questions    | Start with user research and test against real queries for >90% accuracy               |
| Choosing hybrid architecture when document-based suffices  | Match architecture to actual query patterns; start simple, add complexity when needed  |
| Launching without freshness monitoring or update schedules | Set up automated freshness checks and scheduled content reviews                        |
| No provenance tracking on knowledge entries                | Always track source URL, timestamp, author, and confidence score                       |
| Duplicate information across sources                       | Establish single source of truth; merge similar entries with conflict resolution rules |
| Perfectionism delaying launch                              | Launch at 80% coverage and iterate based on real usage data                            |

## Delegation

- **Audit existing knowledge sources and classify content types**: Use `Explore` agent to inventory documents, assess quality, and identify gaps
- **Implement end-to-end KB pipeline with storage and retrieval**: Use `Task` agent to deploy database, configure search, and run quality checks
- **Design KB architecture and governance model**: Use `Plan` agent to select between document-based, entity-based, or hybrid approaches

## References

- [Architecture and Types](references/architecture.md) -- KB types, decision framework, knowledge classification
- [Curation and Ingestion](references/curation.md) -- extraction, cleaning, deduplication, provenance tracking
- [Storage and Retrieval](references/storage.md) -- database selection, interfaces, technology stacks
- [Quality Control](references/quality-control.md) -- metrics, validation strategies, continuous monitoring
- [Versioning](references/versioning.md) -- snapshot, event-sourced, and git-style approaches
- [Governance](references/governance.md) -- maintenance schedules, roles, change processes
