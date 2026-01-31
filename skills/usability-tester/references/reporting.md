---
title: Reporting
description: Usability test report template, findings structure, key insights format, stakeholder presentation tips, and recommended actions with prioritization
tags:
  [
    reporting,
    template,
    insights,
    recommendations,
    test-report,
    stakeholders,
    prioritization,
  ]
---

# Reporting

## Report Structure

A usability test report serves two audiences: the immediate team that needs to fix issues, and stakeholders who need to understand the business impact.

```yaml
Report Sections: 1. Executive Summary (1 page)
  2. Test Overview (objectives, methodology, participants)
  3. Task Results (per-task metrics and findings)
  4. Issue List (all issues with severity ratings)
  5. Key Insights (patterns across tasks)
  6. Recommendations (prioritized action items)
  7. Appendix (raw data, session recordings, SUS scores)
```

## Executive Summary

Write this last. It should stand alone for stakeholders who read nothing else.

```yaml
Template:
  Purpose: [Why the test was conducted]
  Method: [Number of participants, testing method, dates]
  Top Finding: [Single most important discovery]
  Overall Score: [SUS score with interpretation]
  Critical Issues: [Count of critical and high severity issues]
  Recommendation: [Single most important next step]

Example:
  Purpose: Evaluate the onboarding flow for new users before launch.
  Method: 8 participants, moderated remote testing, January 15-17.
  Top Finding: 6 of 8 users could not find the team invite feature.
  Overall Score: SUS 62 (below average, needs improvement).
  Critical Issues: 2 critical, 3 high severity.
  Recommendation: Redesign the invite flow before launch.
```

## Test Overview Section

```yaml
Test Details:
  Objectives:
    - 'Can new users complete onboarding in under 5 minutes?'
    - 'Can users find and use the team invite feature?'
    - 'Do users understand the difference between workspaces and projects?'

  Methodology: Moderated remote usability testing with think-aloud protocol

  Participants:
    Total: 8
    Profile: New users, age 25-45, tech-savvy professionals
    Recruitment: UserTesting.com panel, screened for no prior product use
    Incentive: $75 gift card per participant

  Tasks Tested: 1. Create a new project
    2. Invite a team member
    3. Assign a task
    4. Export project data
    5. Change account settings

  Test Environment: Production application, Chrome browser, participant's own device
```

## Task Results Template

Report each task with quantitative metrics and qualitative observations.

```yaml
Task: "Create a new project"
  Success Rate: 87.5% (7/8 completed without help)
  Median Time: 1m 24s
  Errors per User: 1.2
  Post-Task Satisfaction: 4.3/5
  SEQ Score: 5.8/7

  Key Observations:
    - 5 users found the "New Project" button immediately
    - 2 users looked in the sidebar first before finding the button
    - 1 user confused "project" with "workspace" and created the wrong item

  Issues Found:
    - "New Project" button not visible without scrolling on small screens (medium)
    - Project vs workspace distinction unclear (high)

Task: "Invite a team member"
  Success Rate: 62.5% (5/8 completed without help)
  Median Time: 2m 45s
  Errors per User: 2.8
  Post-Task Satisfaction: 3.1/5
  SEQ Score: 3.9/7

  Key Observations:
    - 6 users expected the invite feature on the project page
    - 3 users looked in account settings before finding team settings
    - 2 users gave up and could not find the feature at all

  Issues Found:
    - Invite button hidden in team settings, not on project page (critical)
    - "Team" and "Members" labels used inconsistently (medium)
```

## Issue List Format

Every issue gets a structured entry for tracking and prioritization.

```yaml
Issue Entry Template:
  ID: [UST-001]
  Title: [Short description]
  Severity: [Critical | High | Medium | Low]
  Impact: [1-3]
  Frequency: [1-3]
  Affected Users: [X/Y participants]
  Task: [Which task(s) affected]
  Description: [What happened and why it is a problem]
  Evidence: [Quote, screenshot, or timestamp reference]
  Recommendation: [Specific fix suggestion]
  Owner: [Team or person responsible]

Example:
  ID: UST-001
  Title: Users cannot find the invite feature
  Severity: Critical
  Impact: 3
  Frequency: 3
  Affected Users: 6/8
  Task: Task 2 (Invite a team member)
  Description: The invite button is located in Team Settings, but users
    expect it on the project page or in the top navigation. Most users
    never found team settings without help.
  Evidence: "I keep looking for an invite button on the project page but
    I can't find one anywhere." (P3, 02:30)
  Recommendation: Add an invite button to the project page header and
    include invite in the top navigation dropdown.
  Owner: Product team
```

## Key Insights

Insights are patterns that emerge across multiple tasks and participants. They go beyond individual issues to reveal systemic problems or opportunities.

```yaml
Insight Format:
  Finding: [What the pattern is]
  Evidence: [Which tasks and how many users]
  Impact: [Why it matters for the business]
  Recommendation: [What to do about it]

Example Insights:
  - Finding: Users expect collaboration features to be accessible from the project page.
    Evidence: 6/8 users looked for invite on the project page (Task 2).
      4/8 users expected task assignment on the project page (Task 3).
    Impact:
      Core collaboration workflows are harder to discover than they should be,
      likely reducing team adoption.
    Recommendation: Surface all collaboration actions on the project page.

  - Finding: Users do not understand the workspace vs project hierarchy.
    Evidence:
      3/8 users created a workspace when asked to create a project (Task 1).
      2/8 users could not explain the difference in the debrief.
    Impact: Confused mental model leads to errors in all project-related tasks.
    Recommendation: Add contextual explanation during onboarding and consider
      whether both concepts are necessary.

  - Finding: Onboarding is effective for basic tasks but fails for team features.
    Evidence: Task 1 success rate 87.5%, but Task 2 only 62.5%.
    Impact: Users can get started but cannot bring their team, reducing product stickiness.
    Recommendation: Add team setup as part of the onboarding flow.
```

## Presenting to Stakeholders

```yaml
Presentation Tips:
  - Lead with the SUS score and overall success rate (executives want numbers)
  - Show 2-3 video clips of users struggling (emotional impact drives action)
  - Focus on business impact: "6/8 users cannot invite teammates" not "invite button is in wrong place"
  - Present recommendations as a prioritized list with effort estimates
  - End with a clear next step and timeline

Slide Structure (15 minutes):
  1. Test overview and goals (1 slide)
  2. Overall metrics: SUS score, average success rate (1 slide)
  3. Top 3 findings with video clips (3 slides)
  4. Issue severity breakdown chart (1 slide)
  5. Prioritized recommendations (1 slide)
  6. Next steps and timeline (1 slide)

Common Objections:
  - "Only 8 users, that's not statistically significant"
    Response: 5 users find 85% of usability issues (Nielsen). We found consistent
    patterns across participants.
  - "Users will figure it out eventually"
    Response: Show time-on-task data and abandonment rates. Every extra second
    of confusion costs conversion.
  - "We already know about that issue"
    Response: Now you have evidence with severity scores to prioritize the fix.
```

## Action Item Prioritization

```yaml
Priority Matrix:
  Fix Now (before release):
    - Critical severity issues (score 9)
    - High severity issues affecting core tasks (score 6-8)

  Fix Next Sprint:
    - High severity issues affecting secondary tasks
    - Medium severity issues on core tasks (score 4-5)

  Backlog:
    - Low severity issues (score 1-3)
    - Medium severity issues on non-critical tasks

  Track and Monitor:
    - Issues that appeared in only 1-2 sessions
    - Issues that may resolve with a broader redesign already planned

Action Item Format:
  - Issue ID and title
  - Severity score
  - Specific fix recommendation
  - Assigned team or owner
  - Target sprint or release
  - Verification plan (how to confirm the fix works)
```
