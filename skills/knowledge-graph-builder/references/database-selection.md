---
title: Database Selection
description: Graph database comparison (Neo4j, Neptune, ArangoDB, TigerGraph) with pros/cons, technology stack recommendations, and Neo4j schema setup
tags: [neo4j, neptune, arangodb, tigergraph, graph-database, cypher]
---

# Database Selection

## Neo4j (Recommended for Most)

- **Pros**: Mature, Cypher query language, graph algorithms, excellent visualization
- **Cons**: Licensing costs for enterprise, scaling complexity
- **Use when**: Complex queries, graph algorithms, team can learn Cypher

## Amazon Neptune

- **Pros**: Managed service, supports Gremlin and SPARQL, AWS integration
- **Cons**: Vendor lock-in, more expensive than self-hosted
- **Use when**: AWS infrastructure, need managed service, compliance requirements

## ArangoDB

- **Pros**: Multi-model (graph + document + key-value), JavaScript queries
- **Cons**: Smaller community, fewer graph-specific features
- **Use when**: Need document DB + graph in one system

## TigerGraph

- **Pros**: Best performance for deep traversals, parallel processing
- **Cons**: Complex setup, higher learning curve
- **Use when**: Massive graphs (billions of edges), real-time analytics

## Technology Stack

```yaml
graph_database: 'Neo4j Community' # or Enterprise for production
vector_integration: 'Pinecone' # For hybrid search
embeddings: 'text-embedding-3-large' # OpenAI
etl: 'Apache Airflow' # For data pipelines
```

## Neo4j Schema Setup

```cypher
// Create constraints for uniqueness
CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT org_name IF NOT EXISTS
FOR (o:Organization) REQUIRE o.name IS UNIQUE;

// Create indexes for performance
CREATE INDEX entity_search IF NOT EXISTS
FOR (e:Entity) ON (e.name, e.type);

CREATE INDEX relationship_type IF NOT EXISTS
FOR ()-[r:RELATED_TO]-() ON (r.type, r.confidence);
```
