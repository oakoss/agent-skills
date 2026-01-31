---
name: scrum-conductor
description: 'Orchestrates AI-enhanced Scrum ceremonies and sprint coordination. Use when running sprint ceremonies, generating automated daily standups, engineering structured tickets, forecasting sprint capacity, or grooming backlogs. Use for fact-based standups, machine-readable tickets, predictive velocity, and backlog deduplication across GitHub Issues, Jira, and Linear.'
license: MIT
metadata:
  author: oakoss
  version: '1.0'
---

# Scrum Conductor

## Overview

Facilitates AI-enhanced Scrum orchestration with automated ticket management and high-velocity sprint coordination. Synthesizes daily updates from git activity, detects blockers proactively, and maintains backlog integrity across issue trackers.

**When to use:** Sprint planning, daily standups, backlog grooming, ticket creation, velocity forecasting, sprint retrospectives, cross-tracker synchronization.

**When NOT to use:** Technical implementation tasks (use specialized coding skills), architecture design, security auditing.

## Quick Reference

| Pattern              | Approach                                                | Key Points                                          |
| -------------------- | ------------------------------------------------------- | --------------------------------------------------- |
| Fact-first standups  | Auto-generate from git logs and PRs                     | Never ask humans for data in commit history         |
| Ticket engineering   | Machine-readable DoD with acceptance criteria           | Binary true/false criteria, implementation pointers |
| Capacity forecasting | Historical cycle time and lead time                     | Factor holidays, context debt, and bottlenecks      |
| Backlog grooming     | AI clustering and deduplication                         | Flag tickets older than 2 sprints for archive       |
| Blocker detection    | Scan PRs, assignments, and dependencies                 | Flag stale PRs, OOO assignees, breaking deps        |
| Parking lot          | Move deep-dives out of standups                         | Standups focus on status and blockers only          |
| Sprint retrospective | AI-driven analysis of sprint patterns                   | Identify bottleneck modules and skill gaps          |
| Escalation tiers     | Tier 1 autonomous, Tier 2 clarification, Tier 3 pairing | Match response to complexity                        |

## Conductor Protocol

1. **Ceremony Initialization**: Identify the current sprint phase (Planning, Daily, Review, Retro)
2. **Telemetry Sync**: Pull recent activity from git commits, PRs, and communication channels
3. **Fact Synthesis**: Generate factual summaries before ceremonies begin
4. **Verification**: Confirm all action items are converted into tracked tickets with clear owners and DoD

## Common Mistakes

| Mistake                                                           | Correct Pattern                                                        |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Asking developers for status updates available in commit logs     | Auto-generate fact summaries from PRs and merges before standups       |
| Creating tickets without a machine-readable Definition of Done    | Every ticket needs explicit acceptance criteria and technical pointers |
| Guessing sprint velocity without historical data                  | Use cycle time, holidays, and context debt to forecast capacity        |
| Letting standups run beyond 15 minutes with deep-dive discussions | Move deep-dives to a parking lot session; standups focus on blockers   |
| Allowing the backlog to grow to 200+ items without pruning        | Auto-flag tickets older than 2 sprints for archive or refactor         |
| Using AI to replace human conversation                            | Use AI to prepare for the conversation, not substitute it              |
| Ignoring team sentiment and morale signals                        | High velocity with low morale is a leading indicator of burnout        |

## Delegation

- **Synthesize daily standup summaries from git activity and PRs**: Use `Task` agent to pull commit logs and generate fact-based updates
- **Cluster and deduplicate backlog tickets across issue trackers**: Use `Explore` agent to scan GitHub Issues, Jira, and Linear for similar or conflicting items
- **Plan sprint capacity and risk assessment using historical velocity**: Use `Plan` agent to model delivery probability and identify at-risk items

## References

- [Automated daily rituals, fact-checking workflows, and blocker detection](references/daily-rituals.md)
- [Ticket engineering standards for humans and AI agents](references/ticket-engineering.md)
- [Predictive velocity, cycle time analysis, and risk forecasting](references/velocity-risk.md)
- [Multi-agent task handoffs, escalation tiers, and AI retrospectives](references/agile-agents.md)
