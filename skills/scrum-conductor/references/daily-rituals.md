---
title: Daily Rituals
description: Automated pre-standup workflows, fact-checking from git logs and CI, blocker detection, status synthesis, and parking lot management
tags: [standup, daily, fact-checking, blocker-detection, parking-lot, git-logs]
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
