---
name: knowledge-graph-builder
description: Design and build knowledge graphs. Use when modeling complex relationships, building semantic search, or creating knowledge bases. Covers schema design, entity relationships, and graph database selection.
version: 1.0.0
---

# Knowledge Graph Builder

Build structured knowledge graphs for enhanced AI system performance through relational knowledge.

**Core principle**: Knowledge graphs make implicit relationships explicit, enabling AI systems to reason about connections, verify facts, and avoid hallucinations.

## When to Use

| Use Knowledge Graphs                                         | Don't Use                                     |
| ------------------------------------------------------------ | --------------------------------------------- |
| Complex entity relationships central to domain               | Simple tabular data (use relational DB)       |
| Verify AI-generated facts against structured knowledge       | Purely document-based search (use vector DB)  |
| Semantic search + relationship traversal                     | No significant relationships between entities |
| Rich interconnections (people, organizations, products)      | Read-heavy workload with no traversal         |
| "How are X and Y related?" queries                           | Team lacks graph modeling expertise           |
| Recommendation systems, fraud detection, pattern recognition |                                               |

## 6-Phase Implementation

| Phase | Focus                | Key Deliverable                              |
| ----- | -------------------- | -------------------------------------------- |
| 1     | Ontology Design      | Entity types, relationship types, properties |
| 2     | Database Selection   | Neo4j / Neptune / Arango / TigerGraph        |
| 3     | Entity Extraction    | NER pipeline, relationship building          |
| 4     | Hybrid Architecture  | Graph + vector search integration            |
| 5     | Query Patterns & API | Cypher queries, API endpoints                |
| 6     | AI Integration       | KG-RAG, hallucination detection              |

## Graph Database Selection

| Database   | Best For                               | Query Language   |
| ---------- | -------------------------------------- | ---------------- |
| Neo4j      | Complex queries, graph algorithms      | Cypher           |
| Neptune    | AWS infra, managed service, compliance | Gremlin / SPARQL |
| ArangoDB   | Multi-model (graph + document + KV)    | AQL (JavaScript) |
| TigerGraph | Massive graphs (billions), real-time   | GSQL             |

## Technology Recommendations

| Scale                | Graph DB               | Vector DB    | ETL     |
| -------------------- | ---------------------- | ------------ | ------- |
| MVP (< 10K entities) | Neo4j Community (free) | OpenAI embed | FastAPI |
| Production (10K–1M)  | Neo4j Enterprise       | Pinecone     | Airflow |
| Enterprise (1M+)     | TigerGraph             | Weaviate     | Kafka   |

## Key Principles

| Principle                       | Detail                                                              |
| ------------------------------- | ------------------------------------------------------------------- |
| Start with ontology             | Define schema before ingesting; changing later is expensive         |
| Entity resolution is critical   | Deduplicate aggressively ("Apple Inc" = "Apple" = "Apple Computer") |
| Confidence scores on everything | Every relationship: 0.0–1.0 score + source                          |
| Build incrementally             | Core entities first, expand over time                               |
| Hybrid architecture wins        | Graph traversal (structured) + vector search (semantic)             |

## Common Use Cases

| Use Case            | Approach                                                 |
| ------------------- | -------------------------------------------------------- |
| Question answering  | Extract entities → traverse graph → return path          |
| Recommendation      | Shared relationships → rank by strength → top-K          |
| Fraud detection     | Model transactions → find suspicious patterns (cycles)   |
| Knowledge discovery | Identify implicit relationships → suggest missing links  |
| Semantic search     | Hybrid vector + graph → expand context via relationships |

## Validation Checklist

| Area              | Criterion                                       |
| ----------------- | ----------------------------------------------- |
| Ontology          | Designed and validated with domain experts      |
| Database          | Selected and set up with constraints/indexes    |
| Entity extraction | Pipeline tested (> 85% accuracy)                |
| Relationships     | Extracted and validated against ontology        |
| Hybrid search     | Graph + vector implemented                      |
| API               | Query endpoints created and documented          |
| AI integration    | RAG or hallucination detection tested           |
| Performance       | Common queries < 100ms                          |
| Operations        | Data quality monitoring, backup/recovery tested |

## Common Mistakes

| Mistake                                                     | Correct Pattern                                                                              |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Ingesting entities before designing the ontology            | Define and validate the ontology with domain experts first; changing later is expensive      |
| Skipping entity resolution and deduplication                | Deduplicate aggressively so "Apple Inc", "Apple", and "Apple Computer" resolve to one entity |
| Omitting confidence scores on relationships                 | Attach a 0.0-1.0 confidence score and source to every relationship                           |
| Using only graph traversal without vector search            | Implement hybrid architecture combining graph traversal with semantic vector search          |
| Building the full graph before validating with real queries | Start with core entities, test against target queries, then expand incrementally             |

## Delegation

- **Extract entities and relationships from unstructured text**: Use `Task` agent to run NER pipelines and build relationship triples
- **Evaluate graph database options for project requirements**: Use `Explore` agent to compare Neo4j, Neptune, ArangoDB, and TigerGraph against scale and query needs
- **Design ontology and hybrid architecture for a new domain**: Use `Plan` agent to define entity types, relationship schemas, and graph-vector integration strategy

## Related Skills

- `rag-implementer` — For hybrid KG+RAG systems
- `agent-patterns` — For knowledge-graph-powered agents

## References

- [Ontology Design](references/ontology-design.md) — Entity types, relationships, properties, RDF schema, validation
- [Database Selection](references/database-selection.md) — Neo4j, Neptune, ArangoDB, TigerGraph comparison and setup
- [Entity Extraction](references/entity-extraction.md) — NER pipeline, relationship extraction, LLM-based extraction
- [Hybrid Architecture](references/hybrid-architecture.md) — Graph + vector integration, hybrid search implementation
- [Query Patterns](references/query-patterns.md) — Cypher queries, API design, common traversal patterns
- [AI Integration](references/ai-integration.md) — KG-RAG, hallucination detection, grounded response generation
