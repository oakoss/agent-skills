---
title: Hybrid Architecture
description: Combined graph database and vector database architecture for knowledge graphs, with hybrid search implementation combining graph traversal and semantic similarity
tags:
  [hybrid-search, vector-database, graph-traversal, embeddings, semantic-search]
---

# Hybrid Knowledge-Vector Architecture

## Architecture

Combine structured graph with semantic vector search for best results:

- **Vector search**: Semantic similarity, flexible queries
- **Graph traversal**: Relationship-based reasoning, context expansion
- **Combined**: Best of both worlds

## Implementation

```python
class HybridKnowledgeSystem:
    def __init__(self):
        self.graph_db = Neo4jConnection()
        self.vector_db = PineconeClient()
        self.embedding_model = OpenAIEmbeddings()

    def store_entity(self, entity: Entity):
        # Store structured data in graph
        self.graph_db.create_node(entity)

        # Store embeddings in vector database
        embedding = self.embedding_model.embed(entity.description)
        self.vector_db.upsert(
            id=entity.id,
            values=embedding,
            metadata=entity.metadata
        )

    def hybrid_search(self, query: str, top_k: int = 10) -> SearchResults:
        # 1. Vector similarity search
        query_embedding = self.embedding_model.embed(query)
        vector_results = self.vector_db.query(
            vector=query_embedding,
            top_k=100
        )

        # 2. Graph traversal from vector results
        entity_ids = [r.id for r in vector_results.matches]
        graph_results = self.graph_db.get_subgraph(entity_ids, max_hops=2)

        # 3. Merge and rank results
        merged = self.merge_results(vector_results, graph_results)
        return merged[:top_k]
```
