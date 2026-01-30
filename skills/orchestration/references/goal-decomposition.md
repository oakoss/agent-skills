---
title: Goal Decomposition
description: HTN planning process, goal analysis, capability matching, precondition validation, scoring and ranking, and decision logging
tags:
  [
    htn,
    goal-decomposition,
    capability-matching,
    preconditions,
    scoring,
    planning,
  ]
---

# Goal Decomposition

For complex goals, decompose into executable capability sequences using Hierarchical Task Network (HTN) planning.

## Process Overview

1. **Analyze goal** -- Extract required and optional effects
2. **Find candidates** -- Query capability graph for capabilities producing desired effects
3. **Validate preconditions** -- Check project state against each capability's requirements
4. **Build HTN plan** -- Order capabilities by dependencies, identify parallel steps, list alternatives
5. **Score and rank** -- Evaluate using weighted utility function
6. **Log decisions** -- Capture rationale, alternatives considered, rejection reasons

## Step 1: Goal Analysis

Break the goal into discrete effects:

```text
Goal: "Build RAG system for documentation search"

Required Effects:
- enables_embedding_generation
- creates_vector_index
- configures_retrieval_pipeline

Optional Effects:
- adds_caching_layer
- implements_reranking

Domains: [rag, api, database]
```

Effects are specific, measurable outcomes. Examples:

- `creates_vector_index`
- `adds_auth_middleware`
- `configures_database`
- `implements_api_endpoint`
- `adds_tests`

## Step 2: Find Candidate Capabilities

For each required effect, find capabilities that produce it:

```text
Effect: creates_vector_index
Candidates:
  - pinecone-integration (managed, low latency)
  - weaviate-setup (self-hosted, more control)
  - qdrant-setup (open source, local dev)
```

## Step 3: Validate Preconditions

Check if current project state satisfies each capability's requirements:

| Check Type      | Example                           | Resolution if Missing |
| --------------- | --------------------------------- | --------------------- |
| File exists     | `package.json` present            | Initialize project    |
| Dependency      | `@tanstack/react-query` installed | Run install command   |
| Environment var | `DATABASE_URL` set                | Add to `.env`         |
| Configuration   | TypeScript config present         | Run init command      |

Capabilities with unsatisfied required preconditions are marked as blocked. Either resolve the precondition or use an alternative capability.

## Step 4: Build HTN Plan

Order capabilities by dependencies and identify parallelism:

```text
Plan for "Build RAG system":
  Step 1: openai-integration     (enables embeddings)     [no deps]
  Step 2: pinecone-setup         (creates vector index)   [no deps]
  Step 3: rag-implementer        (retrieval pipeline)     [depends on 1, 2]

Parallel steps: [[1, 2]]  -- Steps 1 and 2 can run simultaneously
```

Each step includes:

- Capability name and effect
- Whether it is required or optional
- Blocked status
- Alternative capabilities
- Dependencies on other steps
- Reasoning for selection

## Step 5: Score and Rank

Evaluate plans using the weighted utility function:

```text
utility = cost_score * 0.3 + risk_score * 0.3 + latency_score * 0.2 + diversity_score * 0.2
```

Score mappings:

| Factor    | Values and Scores                                     |
| --------- | ----------------------------------------------------- |
| Cost      | free=1.0, low=0.8, medium=0.5, high=0.2               |
| Latency   | instant=1.0, fast=0.7, slow=0.3                       |
| Risk      | safe=1.0, low=0.8, medium=0.5, high=0.2, critical=0.0 |
| Diversity | min(unique_domains / 5, 1.0)                          |

Modifiers:

- **Cooldown penalty**: Capability used within 3 steps gets -30%
- **Novelty bonus**: Capability not yet in plan gets +20%

## Step 6: Decision Logging

Every plan must include a decision log:

```text
Decision Log:
  Goal: "Build RAG system"
  Selected: pinecone-integration (score: 0.78)
  Alternatives considered:
    - weaviate-setup (score: 0.72, rejected: higher operational cost)
    - qdrant-setup (score: 0.65, rejected: requires self-hosting)
  Precondition checks: all passed
  Reasoning: Managed service reduces operational overhead
```

Log fields: goal, timestamp, selected capabilities, alternatives with scores and rejection reasons, precondition results, overall reasoning.
