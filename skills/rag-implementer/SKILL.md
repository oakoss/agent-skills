---
name: rag-implementer
description: Implement retrieval-augmented generation systems. Use when building knowledge-intensive applications, document search, Q&A systems, or need to ground LLM responses in external data. Covers embedding strategy, vector stores, retrieval pipelines, and evaluation.
version: 1.0.0
---

# RAG Implementer

Build production-ready retrieval-augmented generation systems. RAG = Retrieval + Context Assembly + Generation. Use RAG when LLMs need access to fresh, domain-specific, or proprietary knowledge not in their training data.

## Overview

Before building RAG, validate the need: try FAQ pages, keyword search, concierge MVP, or simple semantic search first. Only proceed with RAG for 50k+ documents with validated user demand and $200-500/month budget.

## Quick Reference

| Phase                     | Goal                            | Key Actions                                               |
| ------------------------- | ------------------------------- | --------------------------------------------------------- |
| 1. Knowledge Base Design  | Structured knowledge foundation | Map sources, define chunking, add metadata                |
| 2. Embedding Strategy     | Semantic understanding          | Select model, benchmark on domain data                    |
| 3. Vector Store           | Scalable storage                | Choose DB, configure index, plan scaling                  |
| 4. Retrieval Pipeline     | Beyond simple similarity        | Hybrid retrieval, query enhancement, re-ranking           |
| 5. Context Assembly       | Optimal LLM context             | Rank, synthesize, compress, mitigate "lost in the middle" |
| 6. Evaluation             | Measure performance             | Precision@K, Recall@K, faithfulness, latency              |
| 7. Production Deploy      | Enterprise reliability          | Containerize, cache, graceful degradation, security       |
| 8. Continuous Improvement | Ongoing enhancement             | Auto-updates, fine-tuning, optimization                   |

| Decision                     | Options                            |
| ---------------------------- | ---------------------------------- |
| Vector DB (managed)          | Pinecone                           |
| Vector DB (self-hosted)      | Weaviate                           |
| Vector DB (lightweight)      | Chroma                             |
| Vector DB (cost-conscious)   | pgvector                           |
| Vector DB (high-performance) | Qdrant                             |
| Embedding (general)          | `text-embedding-3-large`           |
| Embedding (code)             | StarEncoder                        |
| Embedding (multilingual)     | `multilingual-e5-large`            |
| Chunking (fixed)             | 500-1000 tokens, 50-100 overlap    |
| Chunking (semantic)          | Paragraph/section/topic boundaries |
| Chunking (recursive)         | Markdown headers, code blocks      |

| Cost Tier                 | Time      | Monthly Cost | Scale            |
| ------------------------- | --------- | ------------ | ---------------- |
| Naive RAG (prototype)     | 1-2 weeks | $50-150      | <10k documents   |
| Advanced RAG (production) | 3-4 weeks | $200-500     | 10k-1M documents |
| Modular RAG (enterprise)  | 6-8 weeks | $500-2000+   | 1M+ documents    |

## Common Mistakes

| Mistake                                            | Correct Pattern                                                                                           |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Building RAG before validating user need           | Try simpler alternatives first (FAQ, keyword search, concierge MVP); only build RAG with validated demand |
| Using a single retrieval method (semantic only)    | Implement hybrid retrieval combining semantic search with keyword (BM25) for better recall                |
| Dumping all available data into the knowledge base | Curate data sources carefully; filter noise, select authoritative content, and maintain quality           |
| Ignoring the "lost in the middle" problem          | Place critical information at the start and end of context; compress mid-section with LLMLingua           |
| Skipping evaluation metrics before production      | Establish baselines for Precision@K, Recall@K, faithfulness, and hallucination rate before deploying      |

## Delegation

- **Discover data sources and assess knowledge base quality**: Use `Explore` agent to catalog documents, evaluate data freshness, and identify authoritative content
- **Implement retrieval pipeline with hybrid search and re-ranking**: Use `Task` agent to build embedding, indexing, retrieval, and evaluation components
- **Design RAG architecture and vector store topology**: Use `Plan` agent to select embedding models, vector databases, chunking strategies, and deployment architecture

## References

- [Architecture patterns and prerequisites](references/architecture-patterns.md)
- [Chunking strategies and knowledge base design](references/chunking-strategies.md)
- [Retrieval methods and pipeline design](references/retrieval-methods.md)
- [Evaluation metrics and quality gates](references/evaluation.md)
- [Production deployment and continuous improvement](references/production-deployment.md)
