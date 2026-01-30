---
title: Metrics and Severity
description: Usability metrics (task success rate, time on task, error rate, satisfaction), System Usability Scale scoring, and issue severity rating formula
tags: [metrics, sus, severity, success-rate, error-rate, satisfaction]
---

# Metrics and Severity

## Task Success Rate

```yaml
Measurement:
  - Completed: User achieved goal without help
  - Partial: User achieved goal with hints
  - Failed: User could not complete task

Calculation: Task Success Rate = (Completed Tasks / Total Attempts) × 100

Target: ≥80% for core tasks
```

## Time on Task

```yaml
Measurement:
  - Start timer when task begins
  - Stop when user completes or gives up

Analysis:
  - Compare to baseline/previous tests
  - Identify outliers (very fast or very slow)

Target: Varies by task complexity
  - Simple task (e.g., log in): <30 seconds
  - Medium task (e.g., create project): 1-2 minutes
  - Complex task (e.g., configure integration): 3-5 minutes
```

## Error Rate

```yaml
Errors:
  - Wrong path taken
  - Incorrect button clicked
  - Had to backtrack
  - Gave up and tried different approach

Calculation: Errors per Task = Total Errors / Number of Users

Target: <2 errors per task
```

## Satisfaction Rating

```yaml
Post-Task Question:
  "How satisfied are you with completing this task?" (1-5 scale)

  1 = Very Dissatisfied
  2 = Dissatisfied
  3 = Neutral
  4 = Satisfied
  5 = Very Satisfied

Target: ≥4.0 average
```

## Issue Severity Rating

Severity = Impact × Frequency

### Impact Scale (1-3)

```yaml
1 - Low Impact:
  - Minor inconvenience
  - User can easily recover
  - Cosmetic issue

2 - Medium Impact:
  - Causes delay or confusion
  - User eventually figures it out
  - Moderate frustration

3 - High Impact:
  - Blocks task completion
  - User cannot proceed without help
  - Critical to core functionality
```

### Frequency Scale (1-3)

```yaml
1 - Rare:
  - Only 1-2 users encountered
  - Edge case
  - Specific conditions

2 - Occasional:
  - 3-5 users encountered
  - Somewhat common
  - Specific user types

3 - Frequent:
  - Most/all users encountered
  - Consistent issue
  - All user types
```

### Combined Severity

```yaml
Critical (8-9):
  - Impact: 3, Frequency: 3
  - Blocks most users
  → Fix immediately before release

High (6-7):
  - Impact: 3, Frequency: 2 OR Impact: 2, Frequency: 3
  - Significant delay or frequent minor issue
  → Fix before release

Medium (4-5):
  - Impact: 2, Frequency: 2 OR Impact: 3, Frequency: 1
  - Minor frustration or rare blocker
  → Fix in next release

Low (1-3):
  - Impact: 1, Frequency: 1-3
  - Cosmetic or rare minor issue
  → Backlog
```

## System Usability Scale (SUS)

10-question survey (post-test, 1-5 Likert scale):

```yaml
Questions (Odd = Positive, Even = Negative):
  1. I think I would like to use this product frequently
  2. I found the product unnecessarily complex
  3. I thought the product was easy to use
  4. I think I would need support to use this product
  5. I found the various functions well integrated
  6. I thought there was too much inconsistency
  7. I imagine most people would learn this quickly
  8. I found the product cumbersome to use
  9. I felt very confident using the product
  10. I needed to learn a lot before getting going

Scoring:
  - Odd questions: Score - 1
  - Even questions: 5 - Score
  - Sum all scores
  - Multiply by 2.5
  - Result: 0-100 score

Interpretation:
  ≥80: Excellent
  68-79: Good (industry average)
  51-67: OK
  <51: Needs significant improvement
```
