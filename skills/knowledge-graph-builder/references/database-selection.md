---
title: Database Selection
description: Graph database comparison (Neo4j, Neptune, ArangoDB, TigerGraph) with pros/cons, query language support, technology stack recommendations, and Neo4j schema setup
tags: [neo4j, neptune, arangodb, tigergraph, graph-database, cypher]
---

# Database Selection

## Neo4j (Recommended for Most Projects)

- **Query language**: Cypher (native), with CalVer versioning (2025.x+)
- **Pros**: Most mature ecosystem, rich graph algorithms library, excellent visualization tools, native vector index support, property sharding for horizontal scaling
- **Cons**: Enterprise licensing costs, Community Edition limited for production scale
- **Use when**: Complex relationship queries, graph algorithms (centrality, community detection, pathfinding), team can learn Cypher
- **Editions**: Community (free, open-source) and Enterprise (commercial license)

```cypher
CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT org_name IF NOT EXISTS
FOR (o:Organization) REQUIRE o.name IS UNIQUE;

CREATE INDEX entity_search IF NOT EXISTS
FOR (e:Entity) ON (e.name, e.type);

CREATE INDEX relationship_type IF NOT EXISTS
FOR ()-[r:RELATED_TO]-() ON (r.type, r.confidence);
```

## Amazon Neptune

- **Query languages**: openCypher, Apache TinkerPop Gremlin, SPARQL (RDF)
- **Pros**: Fully managed, serverless scaling, Multi-AZ high availability, GraphRAG integration with Amazon Bedrock, GraphStorm for graph ML
- **Cons**: AWS vendor lock-in, higher cost than self-hosted, limited graph algorithm library compared to Neo4j
- **Use when**: AWS infrastructure, need managed service, compliance requirements, want GraphRAG with Bedrock
- **Products**: Neptune Database (OLTP, up to 100K queries/sec) and Neptune Analytics (in-memory analytics on large datasets)

```text
Neptune supports three query languages:
- openCypher: Property graph queries (similar to Neo4j Cypher)
- Gremlin: Apache TinkerPop traversal language
- SPARQL: W3C standard for RDF graphs
```

## ArangoDB

- **Query language**: AQL (ArangoDB Query Language, SQL-like)
- **Pros**: True multi-model (graph + document + key-value) in one engine, single query language for all models, flexible schema
- **Cons**: Smaller community than Neo4j, fewer graph-specific algorithms, BUSL-1.1 license from v3.12+ (free Community Edition includes all features but has commercial use restrictions above 100 GiB)
- **Use when**: Need document store and graph in one system, want to avoid managing multiple databases

```text
AQL supports graph, document, and key-value operations:
- Graph: TRAVERSAL, SHORTEST_PATH, K_SHORTEST_PATHS
- Document: INSERT, UPDATE, REPLACE, REMOVE, UPSERT
- Full-text: ANALYZER, SEARCH with ArangoSearch
```

## TigerGraph

- **Query languages**: GSQL (native), OpenCypher, ISO GQL
- **Pros**: Fastest for deep traversals and massive graphs, parallel processing, free Community Edition (16 CPUs, 200 GB graph + 100 GB vector storage), native hybrid vector+graph search
- **Cons**: Steeper learning curve, smaller ecosystem, company has undergone significant organizational changes
- **Use when**: Billions of edges, real-time analytics, deep multi-hop traversals, fraud detection at scale

```text
TigerGraph query language support:
- GSQL: Native, most powerful for TigerGraph-specific features
- OpenCypher: Compatible with Neo4j-style queries
- ISO GQL: Emerging standard for graph query languages
```

## Technology Stack by Scale

| Scale                | Graph DB                    | Vector Integration  | ETL               |
| -------------------- | --------------------------- | ------------------- | ----------------- |
| MVP (< 10K entities) | Neo4j Community (free)      | OpenAI embeddings   | FastAPI / scripts |
| Production (10K-1M)  | Neo4j Enterprise or Neptune | Pinecone / Weaviate | Apache Airflow    |
| Enterprise (1M+)     | TigerGraph or Neptune       | Weaviate / Qdrant   | Kafka + Airflow   |

## Selection Decision Matrix

| Factor           | Neo4j             | Neptune         | ArangoDB           | TigerGraph        |
| ---------------- | ----------------- | --------------- | ------------------ | ----------------- |
| Query complexity | Excellent         | Good            | Good               | Excellent         |
| Managed service  | Aura (cloud)      | Fully managed   | ArangoGraph        | Savanna (cloud)   |
| Graph algorithms | Extensive (GDS)   | Limited         | Basic              | Built-in          |
| Multi-model      | No (graph only)   | No (graph only) | Yes (graph+doc+KV) | No (graph+vector) |
| Vector search    | Native (2025.x+)  | Via Bedrock     | Via ArangoSearch   | Native hybrid     |
| Open source      | Community Edition | No              | BUSL-1.1           | Community Edition |
| Learning curve   | Moderate (Cypher) | Moderate        | Low (SQL-like AQL) | High (GSQL)       |

## Setup Checklist

1. Define scale requirements (entity count, query volume, traversal depth)
2. Evaluate infrastructure constraints (cloud provider, managed vs self-hosted)
3. Assess team expertise (Cypher, Gremlin, SQL, GSQL)
4. Test with representative queries on sample data
5. Configure constraints and indexes before bulk loading
6. Set up monitoring for query performance and memory usage
