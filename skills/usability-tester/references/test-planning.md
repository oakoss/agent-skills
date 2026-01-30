---
title: Test Planning
description: Usability test planning including objectives, research questions, recruitment criteria, incentives, and task scenario templates with good and bad examples
tags: [test-planning, objectives, recruitment, task-scenarios, participants]
---

# Test Planning

## Define Test Objectives

```yaml
Good Objectives:
  - "Can users complete onboarding in <5 minutes?"
  - "Can users find and use the export feature?"
  - "Do users understand the pricing page?"

Bad Objectives:
  - "Test the UI" (too vague)
  - "See if users like it" (subjective, not behavioral)
```

## Research Questions

```yaml
Examples:
  - Where do users get stuck during sign-up?
  - Can users find the settings page?
  - Do users understand what each tier includes?
  - What errors do users encounter?
```

## Identify Core Tasks

Choose 3-5 tasks that represent key user journeys:

```yaml
Example Tasks (Project Management Tool): 1. Sign up and create account
  2. Create your first project
  3. Invite a team member
  4. Assign a task to someone
  5. Export project data
```

## Recruit Participants

```yaml
Sample Size:
  - 5-8 users per persona
  - After 5 users, diminishing returns (Nielsen's research)
  - Test in waves: 5 users → fix issues → test 5 more

Recruitment Criteria:
  - Match target persona
  - Haven't used product before (for onboarding tests)
  - Or: Active users (for feature tests)

Incentives:
  - $50-100 per hour (B2C)
  - $100-200 per hour (B2B professionals)
  - Gift cards work well
```

## Task Scenario Template

```yaml
Scenario: [Context/Motivation]
Goal: [What they need to accomplish]
Success Criteria: [How to know they completed it]

Example:
  Scenario: You're preparing for a client meeting tomorrow and need to review past conversations.
  Goal: Find all conversations with "Acme Corp" from the last 30 days
  Success Criteria: User successfully uses search/filter to find conversations
```

### Good vs Bad Scenarios

Good task scenario:

```text
"Your team is launching a new project next week. Create a project
called 'Q2 Launch' and invite john@example.com to collaborate."
```

Why it works: realistic context, clear goal, natural language, doesn't give step-by-step instructions.

Bad task scenario:

```text
"Click the 'New Project' button, then enter 'Q2 Launch', then
click Settings, then click Invite, then enter email."
```

Why it fails: step-by-step instructions, no context, doesn't test discoverability.
