---
title: Quality Control
description: Knowledge base quality metrics, validation strategies with test questions, human review, automated checks, and continuous monitoring
tags: [knowledge-base, quality, validation, metrics, monitoring, testing]
---

# Quality Control

## Quality Metrics

| Metric         | Description                         | Target   |
| -------------- | ----------------------------------- | -------- |
| Accuracy       | % correct answers to test questions | >90%     |
| Coverage       | % user questions answerable         | >80%     |
| Freshness      | Average age of knowledge            | <30 days |
| Consistency    | % without conflicts/contradictions  | >95%     |
| Source quality | % from authoritative sources        | >90%     |

## Validation Strategies

### Test Question Sets

Create 100+ test questions with known correct answers:

```ts
interface TestQuestion {
  question: string;
  expected_answer: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
}
```

### Human Review

- Sample random knowledge entries
- Subject matter expert validation
- User feedback loops

### Automated Checks

| Check               | Purpose                     |
| ------------------- | --------------------------- |
| Duplicate detection | Find near-identical entries |
| Conflict detection  | Find contradictory facts    |
| Staleness detection | Flag outdated information   |
| Citation validation | Verify sources still exist  |

## Continuous Monitoring

```ts
interface KBHealthMetrics {
  accuracy_score: number;
  coverage_score: number;
  freshness_score: number;
  consistency_score: number;
  user_satisfaction: number;
}
```

## User Satisfaction Targets

| Metric                       | Target |
| ---------------------------- | ------ |
| Query relevance (user-rated) | >85%   |
| Users finding KB valuable    | >80%   |
| Median query time            | <100ms |
| Uptime                       | >99.9% |
