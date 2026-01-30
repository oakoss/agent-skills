---
title: Ontology Design
description: Entity types, relationship types, properties, RDF/Turtle schema examples, and ontology validation checklist for knowledge graphs
tags: [ontology, rdf, entities, relationships, schema-design]
---

# Ontology Design

## Entity Types (Nodes)

Common entity types: Person, Organization, Location, Product, Concept, Event, Document.

## Relationship Types (Edges)

- **Hierarchical**: IS_A, PART_OF, REPORTS_TO
- **Associative**: WORKS_FOR, LOCATED_IN, AUTHORED_BY, RELATED_TO
- **Temporal**: CREATED_ON, OCCURRED_BEFORE, OCCURRED_AFTER

## Properties (Attributes)

- **Node properties**: id, name, type, created_at, metadata
- **Edge properties**: type, confidence, source, timestamp

## RDF/Turtle Example

```turtle
@prefix : <http://example.org/ontology#> .

:Person a owl:Class ;
    rdfs:label "Person" .

:Organization a owl:Class ;
    rdfs:label "Organization" .

:worksFor a owl:ObjectProperty ;
    rdfs:domain :Person ;
    rdfs:range :Organization ;
    rdfs:label "works for" .
```

## Validation

- Entities cover all domain concepts
- Relationships capture key connections
- Ontology reviewed with domain experts
- Classification hierarchy defined (is-a relationships)
