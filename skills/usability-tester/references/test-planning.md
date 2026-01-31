---
title: Test Planning
description: Usability test planning including objectives, research questions, recruitment criteria, screening, incentives, task scenario templates, and pilot testing
tags:
  [
    test-planning,
    objectives,
    recruitment,
    task-scenarios,
    participants,
    screening,
    pilot,
  ]
---

# Test Planning

## Define Test Objectives

Objectives must be behavioral and measurable, not subjective.

```yaml
Good Objectives:
  - "Can users complete onboarding in under 5 minutes?"
  - "Can users find and use the export feature without hints?"
  - "Do users understand what each pricing tier includes?"
  - "Can users recover from a payment error without contacting support?"

Bad Objectives:
  - "Test the UI" (too vague, no success criteria)
  - "See if users like it" (subjective, not behavioral)
  - "Validate the new design" (confirmation bias framing)
  - "Check if it works" (not specific enough to measure)
```

## Research Questions

Research questions identify specific unknowns the test should resolve.

```yaml
Navigation:
  - Can users find the settings page from the dashboard?
  - Where do users expect account management features to live?

Task Completion:
  - Where do users get stuck during sign-up?
  - What errors do users encounter when creating a project?
  - Can users complete checkout without abandoning the cart?

Comprehension:
  - Do users understand the difference between workspaces and projects?
  - Do users understand what each plan tier includes?

Recovery:
  - Can users recover from a failed payment?
  - Do users know how to undo a destructive action?
```

## Identify Core Tasks

Choose 3-5 tasks that represent key user journeys. Order them from simple to complex to build participant confidence.

```yaml
Example Tasks (Project Management Tool): 1. Sign up and create your account
  2. Create your first project
  3. Invite a team member to collaborate
  4. Assign a task to someone on your team
  5. Export project data as a CSV file

Task Selection Criteria:
  - Covers the critical path (what most users must do)
  - Includes at least one discoverability task (find a hidden feature)
  - Includes at least one error recovery task
  - Avoids tasks that require prior domain knowledge
  - Each task is independent (failure on one does not block the next)
```

## Task Scenario Template

Scenarios provide realistic context without revealing the solution path.

```yaml
Template:
  Context: [Why the user needs to do this]
  Goal: [What they need to accomplish]
  Success Criteria: [How to know they completed it]
  Time Limit: [Maximum before marking abandoned]

Example:
  Context: You are preparing for a client meeting tomorrow and need to review past conversations.
  Goal: Find all conversations with "Acme Corp" from the last 30 days.
  Success Criteria: User successfully uses search or filter to find the conversations.
  Time Limit: 3 minutes
```

### Good vs Bad Scenarios

Good task scenario:

```text
"Your team is launching a new project next week. Create a project
called 'Q2 Launch' and invite john@example.com to collaborate."
```

Why it works: realistic context, clear goal, natural language, tests discoverability without giving step-by-step instructions.

Bad task scenario:

```text
"Click the 'New Project' button, then enter 'Q2 Launch', then
click Settings, then click Invite, then enter the email."
```

Why it fails: step-by-step instructions remove discoverability testing, no context for user motivation, user just follows orders.

## Recruit Participants

```yaml
Sample Size:
  - 5-8 users per persona for moderated testing
  - 20-50 users for unmoderated testing
  - After 5 users, diminishing returns on new findings (Nielsen)
  - Test in waves: 5 users, fix top issues, test 5 more

Recruitment Criteria:
  - Match target persona demographics and technical proficiency
  - Have not used the product before (for onboarding tests)
  - Active users with 1-3 months experience (for feature tests)
  - Mix of technical skill levels within the persona
  - Exclude UX professionals (they behave differently)

Incentives:
  - B2C: $50-100 per hour
  - B2B professionals: $100-200 per hour
  - Gift cards work well for remote sessions
  - Pay even if participant cannot complete the test
```

## Screening Questionnaire

Screen participants before scheduling to ensure they match the target persona.

```yaml
Screening Questions:
  - "How often do you use [product category] tools?" (daily/weekly/monthly/never)
  - "What is your role?" (match target persona)
  - "Have you used [product name] before?" (exclude for onboarding tests)
  - "What device do you primarily use for work?" (match test environment)
  - "Are you comfortable sharing your screen during a video call?" (remote tests)

Disqualification Criteria:
  - Works in UX, design, or usability (unless testing for expert users)
  - Has participated in a test for this product in the last 6 months
  - Does not match the target persona demographics
  - Cannot commit to the full session duration
```

## Pilot Testing

Run 1-2 pilot sessions before the real test to catch problems with the test itself.

```yaml
Pilot Checklist:
  - Task scenarios are clear and unambiguous
  - Time limits are realistic (not too short or too long)
  - Recording setup works (screen, audio, camera)
  - Think-aloud instructions are understood
  - Post-task questions flow naturally
  - Session fits within the scheduled time slot
  - Prototype or product is stable enough to test

Common Pilot Findings:
  - Tasks are too easy or too hard
  - Scenario wording reveals the answer
  - Time limits are unrealistic
  - Technical setup has friction (screen sharing, recording)
  - Session runs over the scheduled time
```

## Test Script Structure

```yaml
Session Structure (60 minutes typical):
  - Welcome and consent (5 minutes)
  - Background questions (5 minutes)
  - Think-aloud instructions (3 minutes)
  - Practice task (2 minutes)
  - Test tasks with post-task questions (35 minutes)
  - SUS questionnaire (5 minutes)
  - Debrief and open questions (5 minutes)

Consent Items:
  - Permission to record screen and audio
  - Permission to share anonymized clips with team
  - Explanation that the product is being tested, not the participant
  - Right to stop at any time without penalty
  - Confirmation that incentive is paid regardless of completion
```
