---
title: Storage and Retrieval
description: Database selection criteria, technology stack overview, and implementation delegation for KB storage
tags:
  [
    knowledge-base,
    storage,
    vector-db,
    graph-db,
    search,
    retrieval,
    pinecone,
    neo4j,
  ]
---

# Storage and Retrieval

## Technology Stacks

| Stack          | Vector DB                    | Graph DB        | Embeddings     | Search                    |
| -------------- | ---------------------------- | --------------- | -------------- | ------------------------- |
| Document-based | Pinecone, Weaviate, pgvector | —               | OpenAI, Cohere | Semantic + keyword hybrid |
| Entity-based   | —                            | Neo4j, ArangoDB | —              | Cypher, AQL               |
| Hybrid         | Any vector DB                | Any graph DB    | OpenAI, Cohere | Combined queries          |

## Selection Criteria

Choose storage based on the architecture decision from [Architecture and Types](architecture.md):

| Architecture   | Primary concern                | Key trade-off                                      |
| -------------- | ------------------------------ | -------------------------------------------------- |
| Document-based | Query latency, embedding cost  | Easy to add content vs hard to query relationships |
| Entity-based   | Graph modeling complexity      | Powerful traversal vs upfront schema design        |
| Hybrid         | Synchronization between stores | Combined strengths vs operational complexity       |

## Implementation Steps

1. Choose database(s) based on KB type
2. Implement search/query layer (vector similarity for documents, graph traversal for entities)
3. Add caching and optimization for common access patterns
4. Target <100ms median query time

> For document-based implementation details (chunking, embeddings, vector store configuration), use the `rag-implementer` skill. For entity-based implementation details (ontology design, entity extraction, graph database setup), use the `knowledge-graph-builder` skill.
