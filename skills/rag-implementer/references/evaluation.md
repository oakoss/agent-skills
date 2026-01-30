---
title: Evaluation Metrics and Quality Gates
description: Retrieval quality metrics, generation quality assessment, system performance targets, and quality gates for production
tags: [evaluation, metrics, quality-gates, precision, recall, faithfulness]
---

# Evaluation Metrics and Quality Gates

## Phase 6: Evaluation and Metrics

**Goal**: Measure RAG system performance comprehensively

### Retrieval Quality

- **Precision@K**: Fraction of top-K results that are relevant
- **Recall@K**: Fraction of relevant docs in top-K
- **MRR (Mean Reciprocal Rank)**: Average rank of first relevant result
- **NDCG**: Ranking quality with graded relevance

### Generation Quality

- **Faithfulness**: Generated content accuracy vs. sources
- **Answer Relevance**: Response relevance to query
- **Context Utilization**: How effectively LLM uses retrieved info
- **Hallucination Rate**: Frequency of unsupported claims

### System Performance

- **End-to-End Latency**: Query to answer (<3 seconds target)
- **Retrieval Latency**: Time to retrieve and rank (<500ms)
- **Token Efficiency**: Information density per token
- **Cost Per Query**: Combined retrieval + generation costs

### Validation

- Baseline metrics established
- A/B testing framework for config comparisons
- Automated evaluation pipeline deployed
- Human evaluation protocols for ground truth

## Quality Gates

### Before Production

- Accuracy >85% on evaluation dataset
- End-to-end latency 95th percentile <5 seconds
- Retrieval latency <500ms

### Ongoing Monitoring

- User satisfaction >4.0/5.0
- Reliability: 99.5% uptime
- Cost: Within 10% of budget

## Critical Success Rules

**Non-Negotiable**:

1. Source attribution for every response
2. Validate generated content against sources (prevent hallucination)
3. Filter sensitive data before retrieval
4. Respond within latency thresholds (<3 seconds)
5. Monitor and optimize costs continuously
6. Comply with security policies
7. Graceful degradation on failures
8. Comprehensive testing before production
