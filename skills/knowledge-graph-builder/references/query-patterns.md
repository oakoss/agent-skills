---
title: Query Patterns
description: Common Cypher query patterns for knowledge graphs including entity lookup, relationship traversal, shortest path, multi-hop queries, recommendations, and API design
tags: [cypher, neo4j, query-patterns, graph-api, traversal]
---

# Query Patterns & API Design

## Common Cypher Patterns

### Find Entity

```cypher
MATCH (e:Entity {id: $entity_id})
RETURN e
```

### Find Relationships

```cypher
MATCH (source:Entity {id: $entity_id})-[r]-(target)
RETURN source, r, target
LIMIT 20
```

### Shortest Path Between Entities

```cypher
MATCH path = shortestPath(
  (source:Person {id: $source_id})-[*..5]-(target:Person {id: $target_id})
)
RETURN path
```

### Multi-Hop Traversal

```cypher
MATCH (p:Person {name: $name})-[:WORKS_FOR]->(o:Organization)-[:LOCATED_IN]->(l:Location)
RETURN p.name, o.name, l.city
```

### Recommendation Query

```cypher
// Find people similar to this person based on shared organizations
MATCH (p1:Person {id: $person_id})-[:WORKS_FOR]->(o:Organization)<-[:WORKS_FOR]-(p2:Person)
WHERE p1 <> p2
RETURN p2, COUNT(o) AS shared_orgs
ORDER BY shared_orgs DESC
LIMIT 10
```

## Knowledge Graph API

```python
class KnowledgeGraphAPI:
    def __init__(self, graph_db):
        self.graph = graph_db

    def find_entity(self, entity_name: str) -> Entity:
        """Find entity by name with fuzzy matching"""
        query = """
        MATCH (e:Entity)
        WHERE e.name CONTAINS $name
        RETURN e
        ORDER BY apoc.text.levenshtein(e.name, $name)
        LIMIT 1
        """
        return self.graph.run(query, name=entity_name).single()

    def find_relationships(self, entity_id: str,
                         relationship_type: str = None,
                         max_hops: int = 2) -> List[Relationship]:
        """Find relationships within specified hops"""
        query = f"""
        MATCH (source:Entity {{id: $entity_id}})
        MATCH path = (source)-[r*1..{max_hops}]-(target)
        RETURN path, relationships(path) AS rels
        LIMIT 100
        """
        return self.graph.run(query, entity_id=entity_id).data()

    def get_subgraph(self, entity_ids: List[str],
                    max_hops: int = 2) -> Subgraph:
        """Get connected subgraph for multiple entities"""
        query = f"""
        MATCH (e:Entity)
        WHERE e.id IN $entity_ids
        CALL apoc.path.subgraphAll(e, {{maxLevel: {max_hops}}})
        YIELD nodes, relationships
        RETURN nodes, relationships
        """
        return self.graph.run(query, entity_ids=entity_ids).data()
```
