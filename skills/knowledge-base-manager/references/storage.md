---
title: Storage and Retrieval
description: Database selection, TypeScript interfaces for document/entity/hybrid KB storage, search implementation, and technology stacks
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

## Document-Based KB Interface

```ts
interface DocumentKB {
  store: 'Pinecone' | 'Weaviate' | 'pgvector';
  chunks: {
    content: string;
    embedding: number[];
    metadata: {
      source: string;
      title: string;
      updated_at: string;
      category: string;
    };
  }[];
}
```

## Entity-Based KB Interface

```ts
interface EntityKB {
  store: 'Neo4j' | 'ArangoDB';
  nodes: {
    id: string;
    type: 'Person' | 'Organization' | 'Product' | 'Concept';
    properties: Record<string, any>;
  }[];
  relationships: {
    from: string;
    to: string;
    type: string;
    properties: Record<string, any>;
  }[];
}
```

## Hybrid KB Interface

```ts
interface HybridKB {
  vectorDB: DocumentKB;
  graphDB: EntityKB;
  linker: {
    linkDocumentToEntities(docId: string): string[];
    linkEntityToDocuments(entityId: string): string[];
  };
}
```

## Technology Stacks

| Stack          | Vector DB                    | Graph DB        | Embeddings     | Search                    |
| -------------- | ---------------------------- | --------------- | -------------- | ------------------------- |
| Document-based | Pinecone, Weaviate, pgvector | —               | OpenAI, Cohere | Semantic + keyword hybrid |
| Entity-based   | —                            | Neo4j, ArangoDB | —              | Cypher, AQL               |
| Hybrid         | Any vector DB                | Any graph DB    | OpenAI, Cohere | Combined queries          |

## Implementation Steps

1. Choose database(s) based on KB type
2. Implement search/query layer (vector similarity for documents, graph traversal for entities)
3. Add caching and optimization for common access patterns
4. Target <100ms median query time
