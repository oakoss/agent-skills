---
title: Ticket Engineering
description: Structured ticket creation for humans and AI agents, user story templates, acceptance criteria standards, estimation techniques, priority frameworks, task breakdown patterns, and Definition of Done
tags:
  [
    tickets,
    acceptance-criteria,
    definition-of-done,
    grooming,
    backlog,
    estimation,
    priority,
    user-stories,
    vertical-slicing,
  ]
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

## User Story Template

The standard user story format ensures every ticket captures role, action, and value:

```markdown
## [FEAT] Export Dashboard as PDF

**As a** billing administrator,
**I want** to export the usage dashboard as a PDF,
**So that** I can share monthly usage reports with stakeholders who do not have app access.

**Context**: Finance team requests monthly PDF reports. Currently they screenshot the dashboard manually.

**Implementation**: Start at `src/features/dashboard/export.ts`. Use the existing `PdfGenerator` utility.

**Acceptance Criteria**:

- [ ] "Export PDF" button visible on dashboard for admin role only
- [ ] PDF includes all visible charts and the date range header
- [ ] PDF file size under 5MB for dashboards with up to 12 months of data
- [ ] Export completes within 10 seconds for standard date ranges
- [ ] Audit log entry created on each export

**Technical Constraints**:

- Must use server-side rendering for PDF (not client-side html2canvas)
- PDF generation must not block the main API thread
```

### Story Anti-Patterns

| Anti-Pattern                              | Problem                       | Fix                                                            |
| ----------------------------------------- | ----------------------------- | -------------------------------------------------------------- |
| "As a developer, I want to refactor..."   | Developer is not a user role  | Frame as the outcome: "As a user, I want faster page loads..." |
| Missing "so that" clause                  | No clear value statement      | If you cannot articulate the value, question the priority      |
| Story is actually an epic                 | Too large for a single sprint | Split into vertical slices                                     |
| Acceptance criteria say "works correctly" | Not binary or verifiable      | Replace with specific, measurable conditions                   |

## Task Breakdown Patterns

### Vertical Slicing

Slice stories vertically through all layers of the stack, not horizontally by layer:

```text
WRONG (horizontal slices):
  Ticket 1: Build the database schema
  Ticket 2: Build the API endpoints
  Ticket 3: Build the frontend UI

RIGHT (vertical slices):
  Ticket 1: User can view their profile (DB + API + UI for read)
  Ticket 2: User can edit their name (DB + API + UI for write)
  Ticket 3: User can upload an avatar (DB + API + UI + storage)
```

Vertical slices deliver working functionality at every step. Horizontal slices deliver nothing until all layers are complete.

### Walking Skeleton Approach

For new features, start with the thinnest possible end-to-end path:

1. **Skeleton ticket**: Hardcoded data flows through all layers (DB → API → UI) with no real logic
2. **Flesh-out tickets**: Replace hardcoded values with real implementations one by one
3. **Polish tickets**: Error handling, edge cases, performance optimization

```markdown
## [FEAT] Walking Skeleton — Checkout Flow

**Acceptance Criteria**:

- [ ] Clicking "Buy" sends a request to `/api/checkout`
- [ ] API returns a hardcoded success response
- [ ] UI shows a confirmation page with the hardcoded order ID
- [ ] No real payment processing, no database writes

**Next tickets will add**: Stripe integration, order persistence, email confirmation
```

### Splitting Techniques

When a story is too large for a single sprint:

| Technique               | When to Use            | Example                                                 |
| ----------------------- | ---------------------- | ------------------------------------------------------- |
| By workflow step        | Multi-step user flow   | "User can add to cart" vs "User can checkout"           |
| By data variation       | Multiple input types   | "Import CSV" vs "Import JSON" vs "Import XML"           |
| By business rule        | Complex validation     | "Validate email format" vs "Validate against blocklist" |
| By platform             | Cross-platform feature | "Search on web" vs "Search on mobile"                   |
| Happy path / edge cases | Any feature            | "Successful payment" vs "Payment failure handling"      |

## Estimation Techniques

### Planning Poker

The team estimates stories using a modified Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21.

```text
Estimation Flow:
  1. Product owner reads the story and answers questions
  2. Each team member privately selects a point value
  3. All values revealed simultaneously
  4. If estimates diverge (e.g., 3 and 13), the highest and lowest explain their reasoning
  5. Re-vote until consensus (within 1 step on the scale)

Time-box: 5 minutes per story. If no consensus, take the higher estimate.
```

### Point Scale Reference

| Points | Meaning                              | Example                                  |
| ------ | ------------------------------------ | ---------------------------------------- |
| 1      | Trivial, well-understood             | Fix a typo, update a config value        |
| 2      | Small, minimal unknowns              | Add a field to an existing form          |
| 3      | Medium, some unknowns                | New API endpoint with validation         |
| 5      | Large, moderate complexity           | New feature with UI, API, and DB changes |
| 8      | Very large, significant unknowns     | Integration with external service        |
| 13     | Should probably be split             | Multi-page flow with complex state       |
| 21     | Must be split before sprint planning | This is an epic, not a story             |

### T-Shirt Sizing

For early-stage estimation when precision is not needed (roadmap planning, epic sizing):

| Size | Relative Effort | Point Equivalent |
| ---- | --------------- | ---------------- |
| XS   | Hours           | 1                |
| S    | 1-2 days        | 2-3              |
| M    | 3-5 days        | 5                |
| L    | 1-2 weeks       | 8-13             |
| XL   | Needs splitting | 21+              |

### Reference Story Calibration

Anchor the team's estimation scale with well-known reference stories:

```markdown
**Team Reference Stories:**

- **1 point**: PROJ-42 "Update footer copyright year" (config change, no tests)
- **3 points**: PROJ-108 "Add email field to settings page" (UI + API + migration + tests)
- **5 points**: PROJ-215 "Implement search with Algolia" (new integration, UI, API, indexing)
- **8 points**: PROJ-301 "OAuth with Google and GitHub" (external APIs, token management, error flows)
```

Re-calibrate reference stories every quarter or when team composition changes significantly.

## Priority Frameworks

### MoSCoW Method

Categorize stories into four buckets for a given release or sprint:

| Category        | Meaning                    | Rule                                |
| --------------- | -------------------------- | ----------------------------------- |
| **Must Have**   | Release fails without it   | No more than 60% of capacity        |
| **Should Have** | Important but not critical | Planned but can slip to next sprint |
| **Could Have**  | Nice to have               | Only if capacity allows             |
| **Won't Have**  | Explicitly out of scope    | Documented so stakeholders know     |

### Value vs Effort Matrix

Plot stories on a 2x2 grid to prioritize visually:

```text
                    High Value
                        │
         Quick Wins     │    Big Bets
        (do first)      │   (plan carefully)
                        │
  Low Effort ───────────┼─────────── High Effort
                        │
         Fill-Ins       │    Money Pit
        (do if idle)    │   (avoid or defer)
                        │
                    Low Value
```

### WSJF (Weighted Shortest Job First)

For teams using SAFe or flow-based prioritization:

```text
WSJF = Cost of Delay / Job Duration

Cost of Delay = User Value + Time Criticality + Risk Reduction

Example:
  Story A: CoD = 8, Duration = 3 → WSJF = 2.67
  Story B: CoD = 5, Duration = 1 → WSJF = 5.00
  → Story B goes first (higher WSJF = higher priority)
```

WSJF favors small, high-value items. This prevents large, medium-value items from monopolizing the sprint.

## Definition of Done Checklist

A story is "done" when all of these are true. The team agrees on this checklist once and applies it to every story:

```markdown
**Definition of Done:**

- [ ] Code reviewed and approved by at least one other developer
- [ ] All acceptance criteria verified (manually or via automated tests)
- [ ] Unit tests written and passing (no decrease in coverage)
- [ ] Integration tests passing in CI
- [ ] No new lint warnings or type errors introduced
- [ ] Documentation updated (API docs, README, inline docs as needed)
- [ ] Deployed to staging and smoke-tested
- [ ] Product owner has accepted the work on staging
- [ ] No known regressions in related features
```

### DoD vs Acceptance Criteria

|             | Definition of Done           | Acceptance Criteria              |
| ----------- | ---------------------------- | -------------------------------- |
| Scope       | Applies to ALL stories       | Specific to ONE story            |
| Who defines | The team, once               | Product owner, per story         |
| Changes     | Rarely (quarterly review)    | Every story                      |
| Example     | "Code reviewed and approved" | "User sees a confirmation email" |

A story meets the Definition of Done AND its acceptance criteria before moving to "Done".
