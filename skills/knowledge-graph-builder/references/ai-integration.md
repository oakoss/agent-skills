---
title: AI Integration
description: Knowledge graph RAG for grounded LLM responses, hallucination detection by verifying claims against graph data, and confidence scoring
tags: [rag, hallucination-detection, grounding, llm-integration, confidence]
---

# AI Integration & Hallucination Prevention

## Knowledge Graph RAG

Use the knowledge graph to ground LLM responses with structured context:

```python
class KnowledgeGraphRAG:
    def __init__(self, kg_api, llm_client):
        self.kg = kg_api
        self.llm = llm_client

    def retrieve_context(self, query: str) -> str:
        # Extract entities from query
        entities = self.extract_entities_from_query(query)

        # Retrieve relevant subgraph
        subgraph = self.kg.get_subgraph(
            [e.id for e in entities],
            max_hops=2
        )

        # Format subgraph for LLM
        context = self.format_subgraph_for_llm(subgraph)
        return context

    def generate_with_grounding(self, query: str) -> GroundedResponse:
        context = self.retrieve_context(query)

        prompt = f"""
        Context from knowledge graph:
        {context}

        User query: {query}

        Answer based only on the provided context. Include source entities.
        """

        response = self.llm.generate(prompt)

        return GroundedResponse(
            response=response,
            sources=self.extract_sources(context),
            confidence=self.calculate_confidence(response, context)
        )
```

## Hallucination Detection

Verify LLM claims against the knowledge graph:

```python
class HallucinationDetector:
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph

    def verify_claim(self, claim: str) -> VerificationResult:
        # Parse claim into (subject, predicate, object)
        parsed_claim = self.parse_claim(claim)

        # Query knowledge graph for evidence
        evidence = self.kg.find_evidence(
            parsed_claim.subject,
            parsed_claim.predicate,
            parsed_claim.object
        )

        if evidence:
            return VerificationResult(
                is_supported=True,
                evidence=evidence,
                confidence=evidence.confidence
            )

        # Check for contradictory evidence
        contradiction = self.kg.find_contradiction(parsed_claim)

        return VerificationResult(
            is_supported=False,
            is_contradicted=bool(contradiction),
            contradiction=contradiction
        )
```
