---
title: Metrics and Severity
description: Usability metrics (task success rate, time on task, error rate, satisfaction), System Usability Scale scoring, single ease question, and issue severity rating formula
tags:
  [
    metrics,
    sus,
    severity,
    success-rate,
    error-rate,
    satisfaction,
    seq,
    benchmarking,
  ]
---

# Metrics and Severity

## Task Success Rate

The most fundamental usability metric. Measures whether users can complete the task at all.

```yaml
Measurement:
  - Completed: User achieved goal without any help
  - Partial: User achieved goal with hints or after errors
  - Failed: User could not complete task or gave up

Calculation: Task Success Rate = (Completed Tasks / Total Attempts) x 100

Targets:
  - Core tasks (sign up, checkout): 90% or higher
  - Secondary tasks (settings, export): 80% or higher
  - Advanced tasks (integrations, admin): 70% or higher

Reporting:
  - Report both unassisted and assisted success rates separately
  - Track partial completions to identify where users need help
  - Compare across participant segments (new vs returning users)
```

## Time on Task

Measures how long users take to complete a task. Longer times indicate confusion or inefficiency.

```yaml
Measurement:
  - Start timer when task instructions are given
  - Stop when user completes the task or gives up
  - Record both completed and abandoned times separately

Analysis:
  - Calculate median time (more robust than mean for small samples)
  - Compare to baseline from previous tests or competitor benchmarks
  - Identify outliers: very fast may indicate skipping, very slow indicates struggle
  - Plot distribution to find bimodal patterns (easy for some, hard for others)

Targets (guidelines, adjust per product):
  - Simple task (log in, toggle setting): under 30 seconds
  - Medium task (create item, fill form): 1-2 minutes
  - Complex task (configure integration, set up workflow): 3-5 minutes

Red Flags:
  - Time increases across test rounds (regression)
  - Wide variance between participants (inconsistent experience)
  - Completed tasks taking 3x or more the expected time
```

## Error Rate

Counts mistakes, wrong paths, and backtracking during task completion.

```yaml
What Counts as an Error:
  - Clicked wrong element
  - Navigated to wrong page
  - Had to backtrack or undo
  - Entered invalid data
  - Gave up and tried a different approach
  - Misinterpreted a label or instruction

Calculation: Errors per Task = Total Errors / Number of Participants

Targets:
  - Simple tasks: 0-1 errors per user
  - Medium tasks: fewer than 2 errors per user
  - Complex tasks: fewer than 3 errors per user

Analysis:
  - Categorize errors by type (navigation, input, comprehension)
  - Map errors to specific interface elements
  - Identify the most common first error (often reveals the root cause)
  - Track error recovery rate (how many users recover without help)
```

## Post-Task Satisfaction

Collected immediately after each task using a standardized scale.

### Single Ease Question (SEQ)

The simplest post-task metric. One question, one number.

```yaml
Question: 'Overall, how easy or difficult was this task?'

Scale: 1 = Very Difficult
  2 = Difficult
  3 = Somewhat Difficult
  4 = Neither Easy nor Difficult
  5 = Somewhat Easy
  6 = Easy
  7 = Very Easy

Interpretation:
  - Average SEQ score across studies: 5.5
  - Below 5.5: task is harder than average, investigate
  - Above 5.5: task is easier than average
  - Below 4.0: significant usability problem
```

### 5-Point Satisfaction Scale

Alternative to SEQ, commonly used for simpler reporting.

```yaml
Question: 'How satisfied are you with completing this task?'

Scale: 1 = Very Dissatisfied
  2 = Dissatisfied
  3 = Neutral
  4 = Satisfied
  5 = Very Satisfied

Target: 4.0 or higher average
```

## System Usability Scale (SUS)

Standardized 10-question post-test survey. Administered after all tasks are complete, not after individual tasks. Produces a score from 0 to 100.

```yaml
Questions (alternate positive and negative):
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

Scoring Steps:
  1. For odd-numbered questions (positive): subtract 1 from the score
  2. For even-numbered questions (negative): subtract the score from 5
  3. Sum all 10 adjusted scores
  4. Multiply by 2.5
  5. Result is a score from 0 to 100

Score Interpretation:
  - 80.3 or above: A grade (top 10% of products)
  - 68-80: B-C grade (average to above average)
  - 51-67: D grade (below average, needs improvement)
  - Below 51: F grade (significant usability problems)
  - Industry average: 68

Percentile Benchmarks:
  - 90th percentile: 80.3
  - 75th percentile: 75.0
  - 50th percentile: 68.0
  - 25th percentile: 51.0

Minimum Sample: 8-12 participants for reliable SUS scores
```

## Issue Severity Rating

### Severity Formula

```text
Severity = Impact x Frequency
```

### Impact Scale (1-3)

```yaml
1 - Low Impact:
  - Minor inconvenience or cosmetic issue
  - User can easily recover or work around it
  - Does not affect task completion
  - Example: slightly confusing label that users figure out quickly

2 - Medium Impact:
  - Causes noticeable delay or confusion
  - User eventually completes the task but with frustration
  - Moderate impact on efficiency
  - Example: important feature buried in unexpected location

3 - High Impact:
  - Blocks task completion for some or all users
  - User cannot proceed without external help
  - Critical to core product functionality
  - Example: submit button does not work, no error feedback on failed action
```

### Frequency Scale (1-3)

```yaml
1 - Rare:
  - Only 1-2 participants encountered the issue
  - Edge case or specific conditions required
  - Affects a small subset of users

2 - Occasional:
  - 3-5 participants encountered the issue
  - Somewhat common, specific user types or paths
  - Affects a moderate portion of users

3 - Frequent:
  - Most or all participants encountered the issue
  - Consistent across user types and approaches
  - Affects nearly all users
```

### Combined Severity Matrix

```yaml
Critical (score 9):
  - Impact 3, Frequency 3
  - Blocks most users from completing a core task
  - Action: Fix immediately, do not release without fix

High (score 6-8):
  - Impact 3 Frequency 2, or Impact 2 Frequency 3, or Impact 3 Frequency 1 (if core task)
  - Significant delay for many users or complete blocker for some
  - Action: Fix before release

Medium (score 4-5):
  - Impact 2 Frequency 2, or Impact 3 Frequency 1
  - Moderate frustration or rare blocker
  - Action: Fix in next release cycle

Low (score 1-3):
  - Impact 1 Frequency 1-3, or Impact 2 Frequency 1
  - Minor inconvenience, cosmetic issue
  - Action: Add to backlog, fix when convenient
```

## Benchmarking and Comparison

```yaml
Tracking Over Time:
  - Test the same tasks with each product release
  - Compare metrics to your own baseline, not just industry averages
  - Track trends: improving, stable, or regressing
  - Flag any metric that drops more than 10% between rounds

Competitor Benchmarking:
  - Run the same tasks on competitor products
  - Compare task success rate, time on task, and SUS scores
  - Identify areas where competitors outperform your product
  - Use findings to prioritize improvements

Statistical Considerations:
  - 5 participants: qualitative patterns, not statistically significant
  - 8-12 participants: SUS scores become reliable
  - 20+ participants: task success rates become statistically meaningful
  - Use confidence intervals when reporting to stakeholders
```
