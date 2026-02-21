---
title: Daily Rituals
description: Automated pre-standup workflows, fact-checking from git logs and CI, blocker detection, status synthesis, parking lot management, sprint planning, retrospectives, backlog refinement, and demo reviews
tags:
  [
    standup,
    daily,
    fact-checking,
    blocker-detection,
    parking-lot,
    git-logs,
    sprint-planning,
    retrospective,
    refinement,
    demo,
  ]
---

# Daily Rituals

## The AI Pre-Standup

The first step in any daily ceremony is automated fact gathering. The orchestrator scans:

- **Git Logs**: What was merged? What is still in PR? What PRs have been open for more than 3 days without review?
- **CI/CD**: Are there any broken builds on the main branch? Any flaky tests trending upward?
- **Tickets**: Which tickets changed status? Which are blocked or stale?

## Status Synthesis

Instead of reading raw lists, the AI generates a contextual summary that highlights what matters:

```markdown
### Daily Update: Sprint Day 7

**Fact Summary:**

- **Done**: 4 PRs merged (auth-refactor, search-index, billing-fix, docs-update)
- **In Progress**: payment-webhooks (80% complete, blocked by staging env config)
- **Blockers**: Rate limit hit on external API (escalated to Ops team)

**Strategic Focus:**
Velocity is on track. The auth module shows increasing "failed quality" labels.
Consider a pairing session to address test coverage gaps.
```

## Blocker Detection

AI identifies hidden blockers that humans often miss:

- A PR that has been open for 3+ days with no review assigned
- A ticket assigned to someone who is currently out of office
- A dependency on a library that released a breaking change
- A CI pipeline that has been failing intermittently on the same test

## The Parking Lot Workflow

The standup is for status updates and blockers. Deep technical discussions move to the parking lot:

- The AI identifies keywords during the standup (refactor, architecture decision, design review) and adds them to a shared document for a post-standup session
- Each parking lot item gets a time-box estimate and an owner
- Items not addressed within 48 hours are converted to tracked tickets

## Sprint Planning Mechanics

### Capacity Calculation

Sprint capacity determines how much work the team can realistically commit to:

```text
Sprint Capacity = Team Members × Available Days × Focus Factor

Example:
  5 developers × 9 working days × 0.7 focus factor = 31.5 available dev-days
```

**Focus factor adjustments:**

| Scenario                            | Focus Factor |
| ----------------------------------- | ------------ |
| Experienced team, stable codebase   | 0.75-0.80    |
| New team or major tech migration    | 0.50-0.60    |
| Standard team with typical meetings | 0.65-0.70    |
| Heavy on-call rotation or support   | 0.50-0.55    |

Subtract planned absences (PTO, holidays, conferences) per person before applying the focus factor.

### Story Point Budgeting

Once capacity is known, map it to story points using the team's historical velocity:

```text
Sprint Budget = Average Velocity (last 3 sprints) adjusted for capacity changes

Example:
  Last 3 sprints: 34, 38, 32 points → Average = 34.7
  This sprint: 1 developer on PTO for 3 days → Reduce by ~12%
  Adjusted budget: ~30 points
```

Pull stories from the top of the prioritized backlog until the budget is filled. Leave a 10-15% buffer for unplanned work and bug fixes.

### Sprint Goal Definition

Every sprint needs a single, clear goal that answers "what are we trying to achieve?":

- **Good**: "Users can complete the checkout flow end-to-end with Stripe integration"
- **Bad**: "Work on payments stuff"
- **Bad**: "Complete PROJ-101, PROJ-102, PROJ-103, PROJ-104"

The sprint goal is NOT a list of tickets. It is the outcome that the collection of tickets delivers. If a story does not contribute to the sprint goal, question whether it belongs in this sprint.

## Retrospective Framework

### Start / Stop / Continue

The simplest and most effective retrospective format:

```markdown
### Sprint 14 Retrospective

**Start:**

- Pair programming on complex tickets (auth module had 3 rework cycles)
- Writing ADRs for architectural decisions before implementation

**Stop:**

- Skipping code review for "small" PRs (2 production bugs from unreviewed changes)
- Scheduling meetings during core coding hours (10am-2pm)

**Continue:**

- Daily async standups in Slack (95% participation rate)
- Feature flagging all new features before release
```

### Action Item Tracking

Retrospective insights are worthless without follow-through:

- Every action item gets an **owner** and a **due date** (default: mid-sprint)
- Action items are tracked as tickets in the same backlog, tagged `retro-action`
- Review previous sprint's action items at the start of each retrospective
- If an action item carries over for 2+ sprints, either escalate or acknowledge it as accepted debt

### Velocity Trending Analysis

Use retrospectives to discuss velocity trends, not just the current sprint:

- **Increasing velocity**: Is the team genuinely faster, or are estimates inflating?
- **Decreasing velocity**: Is technical debt accumulating? Are there new team members ramping up?
- **Erratic velocity**: Are scope changes mid-sprint causing churn?

Compare committed vs completed points over the last 5 sprints to identify patterns.

## Backlog Refinement

### When to Refine

Schedule 1-2 refinement sessions per sprint, each 30-60 minutes:

- **Mid-sprint session**: Refine stories for the next sprint
- **Late-sprint session**: Final grooming before sprint planning

Refinement is NOT planning. The goal is to make stories "ready" so planning is efficient.

### What to Refine

Each story in refinement should be evaluated for:

- **Acceptance criteria**: Are they binary (yes/no verifiable)?
- **Estimation**: Does the team agree on the size?
- **Dependencies**: Are external dependencies identified and tracked?
- **Testability**: Can QA write test cases from the acceptance criteria alone?
- **Implementation pointers**: Are relevant files, APIs, or interfaces referenced?

### Definition of Ready Checklist

A story is ready for sprint planning when all criteria are met:

```markdown
**Definition of Ready:**

- [ ] User story follows "As a [role], I want [feature], so that [benefit]" format
- [ ] Acceptance criteria are binary and independently verifiable
- [ ] Story is estimated by the team (not just one person)
- [ ] Dependencies are identified and either resolved or tracked
- [ ] UI mockups or wireframes attached (if applicable)
- [ ] Technical constraints documented (performance budgets, API limits)
- [ ] Story fits within a single sprint (if not, split it)
```

Stories that fail the Definition of Ready checklist go back to the product owner for clarification before entering a sprint.

## Demo and Sprint Review

### Stakeholder-Friendly Format

Sprint reviews are for stakeholders, not developers. Structure the demo around outcomes:

```markdown
### Sprint 14 Review

**Sprint Goal:** Users can complete checkout with Stripe integration

**Completed (Demo Order):**

1. [DEMO] Checkout flow walkthrough (live demo on staging)
2. [DEMO] Payment confirmation email with receipt
3. [SLIDE] Stripe webhook reliability metrics (99.8% delivery rate)
4. [SKIP] Internal refactor of billing module (no visible change)

**Not Completed:**

- Subscription management (carried to Sprint 15, blocked by Stripe API approval)

**Key Metrics:**

- 32 of 34 story points completed (94%)
- 0 production incidents
- 2 tech debt items addressed
```

Demo items that have visible user impact first. Internal refactors and infrastructure work get a brief mention, not a walkthrough.

### Feedback Capture

Capture stakeholder feedback in a structured format during the review:

| Feedback                             | Source       | Type            | Action                                       |
| ------------------------------------ | ------------ | --------------- | -------------------------------------------- |
| "Can we add Apple Pay?"              | Product lead | Feature request | Create ticket, prioritize in next refinement |
| "Checkout is slow on mobile"         | QA           | Bug report      | Create ticket, investigate before Sprint 15  |
| "Love the confirmation email design" | Design lead  | Positive        | No action needed                             |

### Decision Log

Track decisions made during sprint reviews so they are not lost:

```markdown
**Decisions — Sprint 14 Review:**

1. Apple Pay integration moves to Q2 roadmap (not Sprint 15)
2. Mobile performance budget set to <2s load time for checkout
3. Subscription management is the Sprint 15 goal
```

Decisions made in meetings without a written record have a habit of being revisited. Write them down, assign owners, and reference them when the topic resurfaces.
