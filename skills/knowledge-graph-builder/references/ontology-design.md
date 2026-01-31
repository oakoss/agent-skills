---
title: Ontology Design
description: Entity types, relationship types, properties, RDF/Turtle schema examples, ontology validation, and design patterns for knowledge graphs
tags: [ontology, rdf, entities, relationships, schema-design]
---

# Ontology Design

## Core Concepts

An ontology defines the vocabulary and structure of a knowledge graph: what types of entities exist, how they relate, and what properties they carry. Design the ontology before ingesting data -- changing it later requires re-processing all entities and relationships.

## Entity Types (Nodes)

Common entity types and their typical properties:

```text
Person       — id, name, title, email, organization
Organization — id, name, type (company/nonprofit/government), industry, founded
Location     — id, name, coordinates, type (city/country/building)
Product      — id, name, version, category, status
Concept      — id, name, definition, domain
Event        — id, name, date, location, participants
Document     — id, title, author, date, content_hash, source_url
```

Define entity types based on domain requirements. Start with 3-5 core types and expand as needed.

## Relationship Types (Edges)

Organize relationships by semantic category:

- **Hierarchical**: IS_A, PART_OF, REPORTS_TO, BELONGS_TO, SUBCATEGORY_OF
- **Associative**: WORKS_FOR, LOCATED_IN, AUTHORED_BY, RELATED_TO, COLLABORATES_WITH
- **Temporal**: CREATED_ON, OCCURRED_BEFORE, OCCURRED_AFTER, STARTED_AT, ENDED_AT
- **Causal**: CAUSED_BY, LEADS_TO, DEPENDS_ON, ENABLES

Every relationship should have a clear semantic meaning. Avoid generic "RELATED_TO" when a more specific type exists.

## Properties (Attributes)

### Node Properties

```python
class EntityProperties:
    id: str              # Unique identifier (UUID or domain-specific)
    name: str            # Human-readable label
    type: str            # Entity type from ontology
    aliases: list[str]   # Alternative names for entity resolution
    created_at: datetime # When entity was added to graph
    source: str          # Where entity was extracted from
    confidence: float    # Extraction confidence (0.0-1.0)
    metadata: dict       # Domain-specific additional properties
```

### Edge Properties

```python
class RelationshipProperties:
    type: str            # Relationship type from ontology
    confidence: float    # Confidence score (0.0-1.0)
    source: str          # Document or system that produced this relationship
    extracted_at: datetime
    evidence: str        # Text snippet supporting the relationship
    weight: float        # Strength or importance (optional)
```

## RDF/Turtle Schema Example

```turtle
@prefix : <http://example.org/ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Entity classes
:Person a owl:Class ;
    rdfs:label "Person" ;
    rdfs:comment "A human individual" .

:Organization a owl:Class ;
    rdfs:label "Organization" ;
    rdfs:comment "A company, institution, or group" .

:Location a owl:Class ;
    rdfs:label "Location" ;
    rdfs:comment "A geographic place or address" .

# Relationship properties
:worksFor a owl:ObjectProperty ;
    rdfs:domain :Person ;
    rdfs:range :Organization ;
    rdfs:label "works for" .

:locatedIn a owl:ObjectProperty ;
    rdfs:domain :Organization ;
    rdfs:range :Location ;
    rdfs:label "located in" .

# Data properties
:hasName a owl:DatatypeProperty ;
    rdfs:domain owl:Thing ;
    rdfs:range xsd:string .

:hasConfidence a owl:DatatypeProperty ;
    rdfs:range xsd:float ;
    rdfs:comment "Confidence score between 0.0 and 1.0" .
```

## Neo4j Property Graph Schema

```cypher
// Define constraints
CREATE CONSTRAINT entity_id IF NOT EXISTS
FOR (e:Entity) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT person_name IF NOT EXISTS
FOR (p:Person) REQUIRE p.name IS NOT NULL;

// Define indexes for common queries
CREATE INDEX entity_type IF NOT EXISTS
FOR (e:Entity) ON (e.type);

CREATE INDEX entity_name_search IF NOT EXISTS
FOR (e:Entity) ON (e.name);

// Example node creation with properties
CREATE (p:Person:Entity {
  id: randomUUID(),
  name: 'Jane Smith',
  type: 'Person',
  aliases: ['J. Smith', 'Jane R. Smith'],
  confidence: 0.95,
  source: 'hr_database'
})

// Example relationship with properties
MATCH (p:Person {name: 'Jane Smith'})
MATCH (o:Organization {name: 'Acme Corp'})
CREATE (p)-[:WORKS_FOR {
  confidence: 0.92,
  source: 'linkedin_scrape',
  since: date('2022-03-15'),
  evidence: 'Senior Engineer at Acme Corp'
}]->(o)
```

## Design Patterns

### Reification (Relationships with Rich Metadata)

When a relationship needs many properties, model it as an intermediate node:

```cypher
// Instead of a simple edge with many properties:
// (person)-[:EMPLOYED_AT {title, start, end, salary}]->(org)

// Reify into an Employment node:
CREATE (e:Employment {
  title: 'Senior Engineer',
  start_date: date('2022-03-15'),
  end_date: null,
  department: 'Engineering'
})

MATCH (p:Person {name: 'Jane Smith'})
MATCH (o:Organization {name: 'Acme Corp'})
CREATE (p)-[:HAS_EMPLOYMENT]->(e)-[:AT_ORGANIZATION]->(o)
```

### Temporal Versioning

Track how relationships change over time:

```cypher
// Add valid_from and valid_to on relationships
MATCH (p:Person {name: 'Jane Smith'})
MATCH (o1:Organization {name: 'OldCorp'})
MATCH (o2:Organization {name: 'NewCorp'})
CREATE (p)-[:WORKS_FOR {valid_from: date('2019-01-01'), valid_to: date('2022-03-01')}]->(o1)
CREATE (p)-[:WORKS_FOR {valid_from: date('2022-03-15'), valid_to: null}]->(o2)
```

## Validation Checklist

- Entity types cover all domain concepts identified in requirements
- Relationship types capture key connections with clear semantics
- Every relationship has a defined domain (source type) and range (target type)
- Properties include confidence scores and source provenance
- Ontology reviewed and validated with domain experts
- Classification hierarchy defined (IS_A relationships)
- No generic "RELATED_TO" where a specific relationship type exists
- Entity resolution aliases defined for common name variations
