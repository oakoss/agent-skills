---
title: Chunking Strategies and Knowledge Base Design
description: Document chunking approaches, embedding model selection, metadata design, and knowledge base curation
tags: [chunking, embeddings, metadata, knowledge-base, vector-store]
---

# Chunking Strategies and Knowledge Base Design

## Phase 1: Knowledge Base Design

**Goal**: Create well-structured knowledge foundation

**Actions**:

- Map data sources (internal: docs, databases, APIs / external: web, feeds)
- Filter noise, select authoritative content (prevent "data dump fallacy")
- Define chunking strategy: semantic chunking based on structure
- Add metadata: tags, timestamps, source identifiers, categories

**Validation**:

- All data sources catalogued and prioritized
- Data quality assessed (accuracy, completeness, freshness)
- Chunking strategy tested with sample documents
- Metadata schema validated for search effectiveness

## Chunking Strategies

### Fixed-Size Chunking

- 500-1000 tokens per chunk
- 50-100 token overlap between chunks
- Simple to implement, works well for uniform content
- Risk: splits may break semantic boundaries

### Semantic Chunking

- Split by paragraph, section headers, or topic boundaries
- Preserves meaning within chunks
- Better for structured documents (technical docs, articles)

### Recursive Chunking

- Split by structure: markdown headers, code blocks, list items
- Falls back to smaller units when chunks are too large
- Best for mixed-format documents

### Contextual Chunking

- Chunk first, then use an LLM to generate a brief context summary for each chunk
- Prepend the summary to the chunk before embedding (e.g., "This chunk discusses authentication in a Node.js API guide")
- Resolves ambiguous references (pronouns, acronyms) that lose meaning when isolated
- Higher computational cost at indexing time but improves retrieval accuracy

### Late Chunking

- Embed the full document first so every token captures complete document context
- Pool token embeddings within chunk boundaries after full-document encoding
- Improves retrieval accuracy by 10-12% on documents with anaphoric references
- More efficient than contextual chunking but may sacrifice some relevance

### Proposition Chunking

- Break content into atomic, self-contained factual statements
- Each proposition stands alone without needing surrounding context
- Best for fact-dense documents (knowledge bases, encyclopedias, technical specs)
- Significantly improves precision for factual queries

## Phase 2: Embedding Strategy

**Goal**: Choose optimal embedding approach for semantic understanding

**Actions**:

- Select embedding model based on domain
- Plan multi-modal needs (text, code, images, tables)
- Decide on fine-tuning: use domain data if general embeddings underperform
- Establish similarity benchmarks

### Model Selection

| Use Case       | Model                    | Dimensions               |
| -------------- | ------------------------ | ------------------------ |
| General text   | `text-embedding-3-large` | 3072 (reducible via API) |
| Cost-optimized | `text-embedding-3-small` | 1536                     |
| Code search    | Voyage Code 3            | 1024-2048                |
| Multilingual   | `multilingual-e5-large`  | 1024                     |
| Multimodal     | Cohere embed-v4          | 1024                     |

Both OpenAI embedding models support Matryoshka dimensionality reduction via the `dimensions` API parameter. For `text-embedding-3-large`, 1024 dimensions offers near-full accuracy at one-third the storage cost.

## Phase 3: Vector Store Architecture

**Goal**: Implement scalable vector database

**Actions**:

- Choose vector DB based on requirements
- Configure index: HNSW for speed, IVF for scale
- Plan scalability: data growth and query volume
- Implement backup, recovery, security

### Vector DB Decision Matrix

| Requirement                       | Recommended     |
| --------------------------------- | --------------- |
| Managed cloud                     | Pinecone        |
| Self-hosted, feature-rich         | Weaviate        |
| Lightweight, local dev            | Chroma          |
| Cost-conscious, existing Postgres | pgvector        |
| High-performance, production      | Qdrant          |
| Billion-scale vectors             | Milvus / Zilliz |

### Index Configuration

- **HNSW**: Best for speed, higher memory usage
- **IVF**: Better for large-scale, requires training step
- **Flat**: Exact search, only viable for small datasets
