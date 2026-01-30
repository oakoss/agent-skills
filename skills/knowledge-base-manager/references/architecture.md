---
title: Architecture and Types
description: Knowledge base types (document, entity, hybrid), decision framework, when to use and not use a KB, and knowledge classification
tags:
  [
    knowledge-base,
    architecture,
    rag,
    knowledge-graph,
    hybrid,
    decision-framework,
  ]
---

# Architecture and Types

## When to Use a Knowledge Base

Use when: factual questions need consistent answers, information changes frequently, multiple sources need unification, provenance tracking is critical, building AI systems needing grounded information, complex domain with interconnected concepts.

Don't use when: static documentation suffices, no maintenance resources available, simple FAQ covers all questions (<50 items), information never changes.

## Document-Based KB (RAG)

Collection of documents, chunked and embedded for semantic search.

Best for: technical documentation, support articles, policy documents, research papers, user manuals.

Strengths: easy to add documents, preserves full context, natural for text-heavy content.

Weaknesses: hard to query relationships, duplicate information across documents, difficult to keep facts consistent.

Implementation: `rag-implementer` skill + vector database.

## Entity-Based KB (Knowledge Graph)

Network of entities (people, places, things) connected by relationships.

Best for: org charts, product catalogs, social networks, recommendation systems, fraud detection, supply chain.

Strengths: excellent for relationship queries, consistent facts (one source of truth), powerful traversal.

Weaknesses: upfront modeling required, harder to add unstructured info, graph query learning curve.

Implementation: `knowledge-graph-builder` skill + graph database.

## Hybrid KB (RAG + Graph)

Documents for unstructured knowledge + graph for structured entities/relationships.

Best for: enterprise knowledge management, research with citations, medical systems, legal systems, e-commerce.

Implementation: both `rag-implementer` + `knowledge-graph-builder` skills.

## Knowledge Classification

| Type         | Description                  | Example                              |
| ------------ | ---------------------------- | ------------------------------------ |
| Factual      | Verifiable facts             | "Product X costs $50"                |
| Procedural   | How-to knowledge             | "How to deploy to production"        |
| Conceptual   | Definitions and explanations | "What is microservices architecture" |
| Relationship | Connections between entities | "Team A reports to Division B"       |
