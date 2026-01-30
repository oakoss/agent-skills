---
title: Velocity and Risk
description: Cycle time analysis, context debt detection, integration friction metrics, probability-based burn-down, and sprint goal forecasting
tags:
  [velocity, cycle-time, lead-time, burn-down, risk-forecasting, context-debt]
---

# Velocity and Risk

## Cycle Time Analysis

Cycle time measures how long a ticket takes from "In Progress" to "Merged". This is the primary velocity metric.

- Flag any ticket that exceeds the team's 90th percentile cycle time
- Track trends over sprints to detect degradation early
- Break down cycle time into phases: coding, review, QA, deployment

## Lead Time

Lead time measures the full duration from ticket creation to deployment. The gap between lead time and cycle time reveals queue and prioritization bottlenecks.

## Context Debt

AI agent performance drops when the project context becomes cluttered or contradictory:

- **Risk Indicator**: An increase in "fixing previous fix" commits
- **Risk Indicator**: Growing number of reopened tickets
- **Remedy**: Schedule a context cleanup sprint to address accumulated inconsistencies, outdated documentation, and conflicting patterns

## Integration Friction

If the time spent in "Ready for Review" is increasing, the review process is a bottleneck:

- Implement automated code review for low-level checks (lint, type errors, formatting)
- Reserve human review for architectural decisions and business logic
- Track review turnaround time as a team metric

## Probability-Based Burn-Down

The burn-down chart includes a probability cone based on historical data:

- "Based on current velocity and remaining work, there is an 85% chance of hitting the sprint goal by Friday"
- Factor in planned absences, holidays, and known blockers
- Update the forecast daily as new data comes in
- Alert the team when probability drops below 60%
