---
title: Velocity and Risk
description: Cycle time analysis, context debt detection, integration friction metrics, probability-based burn-down, sprint goal forecasting, sprint metrics dashboard, risk management, distributed team patterns, and release planning
tags:
  [
    velocity,
    cycle-time,
    lead-time,
    burn-down,
    risk-forecasting,
    context-debt,
    metrics,
    distributed-teams,
    release-planning,
    dependency-mapping,
  ]
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

## Sprint Metrics Dashboard

### Core Metrics

Track these four metrics every sprint to build a complete velocity picture:

| Metric     | What It Measures               | How to Calculate                            | Healthy Range                            |
| ---------- | ------------------------------ | ------------------------------------------- | ---------------------------------------- |
| Velocity   | Work completed per sprint      | Sum of story points in "Done"               | Stable ±15% across sprints               |
| Burndown   | Remaining work over time       | Total points minus completed, plotted daily | Tracks close to the ideal line           |
| Burnup     | Scope and completion over time | Two lines: total scope and completed work   | Completion line trends toward scope line |
| Throughput | Number of items completed      | Count of tickets moved to "Done" per sprint | Increasing or stable                     |

### Velocity Chart

```text
Points
  40 │          ╭─╮
  35 │    ╭─╮   │ │  ╭─╮
  30 │ ╭─╮│ │╭─╮│ │  │ │
  25 │ │ ││ ││ ││ │╭─╮ │
  20 │ │ ││ ││ ││ ││ ││ │
     └─┴─┴┴─┴┴─┴┴─┴┴─┴┴─┴──
      S8  S9  S10 S11 S12 S13

Average velocity (last 3): 34 points
Trend: Stable (within ±10%)
```

Use the average of the last 3 sprints for planning. Ignore outlier sprints (holidays, team changes) when calculating averages.

### Burndown vs Burnup

**Burndown** shows remaining work decreasing over the sprint. It is simple but hides scope changes.

**Burnup** shows two lines: total scope and completed work. When the scope line moves up mid-sprint, the burnup chart makes that visible. Prefer burnup for sprints where scope changes are common.

```text
Burnup Chart — Sprint 13
Points
  40 │                    ╱── Total Scope (grew mid-sprint)
  35 │              ╱────╱
  30 │        ╱────╱
  25 │  ╱────╱            ╱── Completed
  20 │─╱            ╱────╱
  15 │        ╱────╱
  10 │  ╱────╱
   5 │─╱
     └────────────────────
      D1  D3  D5  D7  D9
```

### Cycle Time Distribution

Track cycle time as a histogram to identify patterns:

```text
Tickets
  12 │  ██
  10 │  ██ ██
   8 │  ██ ██ ██
   6 │  ██ ██ ██ ██
   4 │  ██ ██ ██ ██ ██
   2 │  ██ ██ ██ ██ ██ ██
     └──────────────────────
      1d  2d  3d  5d  8d  13d+

Median: 3 days | 85th percentile: 5 days | Outliers: 2 tickets at 13+ days
```

Investigate any ticket beyond the 85th percentile. These outliers often reveal systemic issues (unclear requirements, dependency bottlenecks, knowledge silos).

## Risk Management

### Dependency Mapping Between Stories

Dependencies within a sprint create critical paths. Map them explicitly:

```text
PROJ-101 (Auth API)
  └─ blocks → PROJ-102 (Login UI)
  └─ blocks → PROJ-103 (OAuth Flow)
                └─ blocks → PROJ-104 (Social Login)

PROJ-105 (DB Migration)
  └─ blocks → PROJ-106 (New Dashboard)
```

**Rules for dependency management:**

- No more than 2 levels of dependency within a sprint
- Stories with 3+ dependents are critical path items — assign the strongest developer
- External dependencies (other teams, third-party APIs) get a risk buffer of +50% estimated time
- If a blocking story slips, immediately re-evaluate all downstream stories

### Critical Path Identification

The critical path is the longest chain of dependent stories in the sprint. If any story on the critical path slips, the sprint goal is at risk.

```text
Sprint Critical Path Analysis:

Path 1: PROJ-101 → PROJ-102 → PROJ-104 (total: 13 points, 3 stories)
Path 2: PROJ-105 → PROJ-106 (total: 8 points, 2 stories)

Critical path: Path 1 (longest chain)
Risk: PROJ-101 is estimated at 5 points and has an external API dependency
Mitigation: Start PROJ-101 on day 1, pair with senior developer
```

### Risk Register

Maintain a living risk register for the sprint:

| Risk                                       | Probability | Impact | Score | Mitigation                                   | Owner         |
| ------------------------------------------ | ----------- | ------ | ----- | -------------------------------------------- | ------------- |
| Stripe API approval delayed                | High        | High   | 9     | Pre-build with mock API, swap when approved  | Backend lead  |
| New developer unfamiliar with auth module  | Medium      | Medium | 4     | Pair programming first 2 days                | Tech lead     |
| CI flaky tests causing merge delays        | Medium      | Low    | 3     | Quarantine flaky tests, fix in parallel      | DevOps        |
| Scope creep from stakeholder demo feedback | Low         | High   | 3     | Defer new requests to next sprint by default | Product owner |

**Risk score** = Probability (1-3) x Impact (1-3). Address scores of 6+ immediately. Monitor scores of 3-5. Accept scores below 3.

### Risk Response Strategies

| Strategy     | When to Use                                | Example                                            |
| ------------ | ------------------------------------------ | -------------------------------------------------- |
| **Avoid**    | Eliminate the risk entirely                | Remove the dependency on the unstable API          |
| **Mitigate** | Reduce probability or impact               | Start the risky story first, add pair programming  |
| **Transfer** | Shift ownership                            | Escalate to the platform team who owns the service |
| **Accept**   | Low impact, not worth the cost to mitigate | Minor UI inconsistency in an internal tool         |

## Distributed Team Patterns

### Async Standups

For teams spanning 3+ timezones, replace synchronous standups with async summaries:

```markdown
### Async Standup Template (Slack / Teams)

**What I completed since last update:**

- Merged PR #234 (search indexing)
- Fixed flaky test in billing module

**What I am working on today:**

- PROJ-108: API endpoint for export feature

**Blockers:**

- None

**Availability:**

- Available 9am-5pm EST, OOO Thursday afternoon
```

Post async standups in a dedicated channel. The AI scrum conductor aggregates updates and flags gaps (missed updates, stale blockers, conflicting work).

### Timezone-Aware Sprint Ceremonies

| Ceremony        | Approach for Distributed Teams                                                      |
| --------------- | ----------------------------------------------------------------------------------- |
| Sprint Planning | Schedule during overlap hours, record for absent members                            |
| Daily Standup   | Async by default, sync only during overlap hours                                    |
| Refinement      | Rotate session times to share the inconvenience                                     |
| Sprint Review   | Record the demo, async feedback form for those who cannot attend                    |
| Retrospective   | Async input collection (Start/Stop/Continue form), sync discussion in overlap hours |

### Overlap Hours Strategy

Identify the window where all (or most) timezones overlap:

```text
Team Distribution:
  US Pacific (UTC-8):  9am-5pm  →  17:00-01:00 UTC
  US Eastern (UTC-5):  9am-5pm  →  14:00-22:00 UTC
  Central Europe (UTC+1): 9am-5pm → 08:00-16:00 UTC
  India (UTC+5:30):    9am-5pm  →  03:30-11:30 UTC

Overlap (US East + Europe): 14:00-16:00 UTC (2 hours)
Overlap (all four): None — use async for India, sync for US+Europe
```

Protect overlap hours for synchronous ceremonies and critical discussions. Do not schedule non-essential meetings during overlap time.

## Release Planning

### Multi-Sprint Roadmap

Plan releases across 3-6 sprints with decreasing confidence:

| Sprint          | Confidence | Content                                |
| --------------- | ---------- | -------------------------------------- |
| Current sprint  | 90%+       | Committed stories with sprint goal     |
| Next sprint     | 70-80%     | Refined stories, tentative sprint goal |
| Sprint +2       | 50-60%     | Estimated epics, rough scope           |
| Sprint +3 to +6 | 30-40%     | Themes and strategic objectives only   |

Update the roadmap every sprint during sprint planning. Stakeholders should see confidence levels, not fixed promises.

### Release Train Concept

For larger teams, coordinate multiple squads releasing on a fixed cadence:

- **Release cadence**: Every 2-4 sprints (e.g., monthly)
- **Feature freeze**: 2-3 days before release for stabilization
- **Release criteria**: All stories meet Definition of Done, no P0/P1 bugs open, staging smoke tests pass
- **Rollback plan**: Feature flags allow disabling individual features without a full rollback

### Feature Flags for Incremental Delivery

Decouple deployment from release using feature flags:

```text
Feature Flag Strategy:

1. Deploy code behind a flag (off by default)
2. Enable for internal team first (dogfooding)
3. Enable for 5% of users (canary release)
4. Monitor error rates and performance for 24-48 hours
5. Ramp to 25% → 50% → 100% over days
6. Remove the flag after full rollout is stable for 1 sprint
```

**Flag hygiene:**

- Every flag has an owner and an expiration date
- Flags older than 2 sprints without progress get flagged in backlog grooming
- Maximum 10 active feature flags at any time (more creates testing complexity)
- Dead flags (fully rolled out or abandoned) are removed as tech debt tickets
