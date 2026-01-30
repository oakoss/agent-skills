---
title: Ticket Engineering
description: Structured ticket creation for humans and AI agents, acceptance criteria standards, implementation pointers, technical constraints, and automatic grooming
tags: [tickets, acceptance-criteria, definition-of-done, grooming, backlog]
---

# Ticket Engineering

## Writing for Two Audiences

Tickets are read by humans and AI agents. They must be precise enough for both.

## The Context Section (Why)

Explain the business or technical reason for the task:

- **Good**: "Needed to comply with new billing meter requirements from the payment provider"
- **Bad**: "Update payment code"

## Implementation Pointers (Starting Point)

For AI agents, provide a clear starting point:

- Relevant file path (e.g., `src/lib/billing.ts`)
- Interface or type name to reference
- Link to external documentation if applicable

## Acceptance Criteria

Must be binary (true/false). Each criterion is independently verifiable:

```markdown
## [FEAT] Implement Usage Dashboard

**Context**: Users need to see their current billing usage.

**Implementation**: Start at `src/pages/dashboard.tsx`. See `UsageMeter` interface.

**Acceptance Criteria**:

- [ ] Users can see their current usage in the dashboard
- [ ] Webhook handles `meter.updated` events
- [ ] 100% test coverage on `calculateBilling()` function
- [ ] RLS policy scoped to authenticated user only
```

## Technical Constraints

Mention explicit boundaries:

- Files or modules that must NOT be changed
- Performance budgets or size limits
- External service rate limits or API version requirements

## Automatic Grooming

Use AI to scan the backlog for quality issues:

- **Ambiguity**: "This ticket has no acceptance criteria, please clarify"
- **Duplication**: "This looks 85% similar to ticket PROJ-456"
- **Staleness**: "This ticket has had no activity for 4+ weeks"
- **Technical Debt**: "This module has not been touched in 4 months and has open issues"
