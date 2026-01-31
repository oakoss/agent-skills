---
title: Hybrid Architecture
description: Combined graph database and vector database architecture for knowledge graphs, hybrid search implementation, ingestion pipeline, and ranking strategies
tags:
  [hybrid-search, vector-database, graph-traversal, embeddings, semantic-search]
---

# Hybrid Knowledge-Vector Architecture

## Why Hybrid

Neither graph traversal nor vector search alone covers all knowledge retrieval needs:

- **Vector search**: Finds semantically similar content even with different wording, handles fuzzy queries
- **Graph traversal**: Follows explicit relationships, provides structured reasoning paths, explains connections
- **Hybrid**: Vector search finds entry points, graph traversal expands context through relationships

## Architecture Overview

```text
                    ┌─────────────┐
                    │   Query     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Router    │
                    └──┬──────┬───┘
                       │      │
              ┌────────▼─┐  ┌─▼────────┐
              │  Vector  │  │   Graph   │
              │  Search  │  │ Traversal │
              └────┬─────┘  └─────┬─────┘
                   │              │
              ┌────▼──────────────▼────┐
              │    Merge & Re-rank     │
              └───────────┬────────────┘
                          │
                   ┌──────▼──────┐
                   │   Results   │
                   └─────────────┘
```

## Dual Storage Implementation

```python
class HybridKnowledgeSystem:
    def __init__(self):
        self.graph_db = Neo4jConnection()
        self.vector_db = PineconeClient()
        self.embedding_model = OpenAIEmbeddings()

    def store_entity(self, entity: Entity):
        self.graph_db.create_node(entity)

        embedding = self.embedding_model.embed(entity.description)
        self.vector_db.upsert(
            id=entity.id,
            values=embedding,
            metadata={
                "type": entity.type,
                "name": entity.name,
                "graph_id": entity.id
            }
        )

    def store_relationship(self, source_id: str, target_id: str,
                          rel_type: str, properties: dict):
        self.graph_db.create_relationship(
            source_id, target_id, rel_type, properties
        )

        rel_text = f"{properties.get('evidence', '')} {rel_type}"
        embedding = self.embedding_model.embed(rel_text)
        self.vector_db.upsert(
            id=f"rel_{source_id}_{target_id}",
            values=embedding,
            metadata={
                "type": "relationship",
                "rel_type": rel_type,
                "source_id": source_id,
                "target_id": target_id
            }
        )
```

## Hybrid Search

```python
class HybridSearch:
    def __init__(self, graph_db, vector_db, embedding_model):
        self.graph = graph_db
        self.vectors = vector_db
        self.embedder = embedding_model

    def search(self, query: str, top_k: int = 10,
               graph_hops: int = 2) -> list[SearchResult]:
        query_embedding = self.embedder.embed(query)
        vector_results = self.vectors.query(
            vector=query_embedding,
            top_k=top_k * 5
        )

        entity_ids = [r.metadata["graph_id"] for r in vector_results.matches
                      if r.metadata.get("type") != "relationship"]

        graph_context = self.graph.get_neighborhood(
            entity_ids[:20],
            max_hops=graph_hops
        )

        return self._merge_and_rank(
            vector_results, graph_context, query, top_k
        )

    def _merge_and_rank(self, vector_results, graph_context,
                        query: str, top_k: int) -> list[SearchResult]:
        scored_results = {}

        for result in vector_results.matches:
            scored_results[result.id] = SearchResult(
                entity_id=result.id,
                vector_score=result.score,
                graph_score=0.0,
                metadata=result.metadata
            )

        for node in graph_context.nodes:
            if node.id in scored_results:
                scored_results[node.id].graph_score = node.centrality
            else:
                scored_results[node.id] = SearchResult(
                    entity_id=node.id,
                    vector_score=0.0,
                    graph_score=node.centrality,
                    metadata=node.properties
                )

        for result in scored_results.values():
            result.combined_score = (
                0.6 * result.vector_score +
                0.4 * result.graph_score
            )

        ranked = sorted(
            scored_results.values(),
            key=lambda r: r.combined_score,
            reverse=True
        )
        return ranked[:top_k]
```

## Ingestion Pipeline

```python
class HybridIngestionPipeline:
    def __init__(self, hybrid_system: HybridKnowledgeSystem,
                 entity_extractor, relationship_extractor):
        self.system = hybrid_system
        self.entity_extractor = entity_extractor
        self.relationship_extractor = relationship_extractor

    def ingest_document(self, document: Document):
        entities = self.entity_extractor.extract(document.text)

        resolved_entities = self._resolve_entities(entities)

        for entity in resolved_entities:
            self.system.store_entity(entity)

        relationships = self.relationship_extractor.extract(
            resolved_entities, document.text
        )

        for rel in relationships:
            self.system.store_relationship(
                source_id=rel.source_id,
                target_id=rel.target_id,
                rel_type=rel.type,
                properties={
                    "confidence": rel.confidence,
                    "source": document.id,
                    "evidence": rel.evidence
                }
            )

    def _resolve_entities(self, entities: list[Entity]) -> list[Entity]:
        resolved = []
        for entity in entities:
            existing = self.system.graph_db.find_by_alias(
                entity.name, entity.type
            )
            if existing:
                existing.aliases.append(entity.name)
                resolved.append(existing)
            else:
                resolved.append(entity)
        return resolved
```

## Query Routing Strategy

Route queries to the appropriate search mode based on query characteristics:

```python
class QueryRouter:
    def route(self, query: str) -> str:
        if self._has_relationship_pattern(query):
            return "graph_first"

        if self._is_semantic_search(query):
            return "vector_first"

        return "hybrid"

    def _has_relationship_pattern(self, query: str) -> bool:
        patterns = [
            "how are .* related",
            "connected to",
            "path between",
            "reports to",
            "works for"
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in patterns)

    def _is_semantic_search(self, query: str) -> bool:
        return len(query.split()) > 10 or "similar to" in query.lower()
```

## Consistency Considerations

- Keep graph and vector stores in sync during writes (store to both atomically or use eventual consistency with reconciliation)
- Embed entity descriptions, not just names, for better semantic matching
- Include relationship evidence text in vector embeddings for relationship search
- Re-embed entities when descriptions change significantly
- Monitor vector-graph ID mapping for orphaned entries
