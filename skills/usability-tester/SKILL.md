---
name: usability-tester
description: Conduct usability tests and identify UX issues through systematic observation. Use when testing user flows, validating designs, identifying friction points, or ensuring users can complete core tasks. Covers test planning, think-aloud protocol, task scenarios, and severity rating.
---

# Usability Tester

Validate that users can successfully complete core tasks through systematic observation.

**Core Principle:** Watch users struggle. Their struggles reveal truth that surveys and analytics cannot.

## Test Planning Checklist

| Phase              | Key Actions                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------------ |
| Objectives         | Define behavioral goals ("Can users complete X in Y minutes?"), not subjective ones ("See if users like it") |
| Research questions | Identify specific unknowns: where do users get stuck, what errors occur, can they find features              |
| Core tasks         | Choose 3-5 tasks representing key user journeys                                                              |
| Recruitment        | 5-8 users per persona; after 5, diminishing returns (Nielsen's research); test in waves                      |
| Incentives         | $50-100/hr B2C, $100-200/hr B2B professionals                                                                |

## Task Scenario Rules

| Do                        | Don't                          |
| ------------------------- | ------------------------------ |
| Provide realistic context | Give step-by-step instructions |
| State clear goal          | Use product-specific jargon    |
| Use natural language      | Reveal UI element names        |
| Test discoverability      | Tell users where to click      |

## Think-Aloud Protocol

| Listen For                     | Reveals           |
| ------------------------------ | ----------------- |
| "I'm looking for..."           | User expectations |
| "I thought this would..."      | Mental models     |
| "This is confusing because..." | Friction points   |
| "I'm not sure if..."           | Uncertainty       |

## Facilitation Rules

| Do                        | Don't                               |
| ------------------------- | ----------------------------------- |
| Observe silently          | Help or explain                     |
| Take notes                | Lead them ("maybe try clicking...") |
| Let them struggle         | Defend design choices               |
| Ask follow-ups AFTER task | Interrupt during task               |

## Metrics

| Metric            | Target                                 | Calculation                        |
| ----------------- | -------------------------------------- | ---------------------------------- |
| Task success rate | ≥80% core tasks                        | Completed / Total attempts × 100   |
| Time on task      | Simple <30s, Medium 1-2m, Complex 3-5m | Start to completion or abandonment |
| Error rate        | <2 per task                            | Total errors / Number of users     |
| Satisfaction      | ≥4.0 average                           | Post-task 1-5 scale                |

## Issue Severity

| Severity | Score                      | Action                         |
| -------- | -------------------------- | ------------------------------ |
| Critical | Impact 3 × Frequency 3 = 9 | Fix immediately before release |
| High     | 6-7                        | Fix before release             |
| Medium   | 4-5                        | Fix in next release            |
| Low      | 1-3                        | Backlog                        |

Impact: 1 (minor inconvenience) → 3 (blocks task). Frequency: 1 (1-2 users) → 3 (most/all users).

## System Usability Scale (SUS)

10-question post-test survey (1-5 Likert). Odd questions positive, even negative. Score: sum adjusted scores × 2.5 → 0-100 scale. ≥80 Excellent, 68-79 Good (industry average), 51-67 OK, <51 Needs improvement.

## Common Pitfalls

| Pitfall                    | Why It Matters                               |
| -------------------------- | -------------------------------------------- |
| Testing with employees     | They know the product too well               |
| Helping users during tasks | Masks real discoverability issues            |
| Only testing happy path    | Misses error and edge case problems          |
| Not enough participants    | 5 minimum per persona for valid findings     |
| Testing but not fixing     | Usability tests are worthless without action |

## Common Mistakes

| Mistake                                                                          | Correct Pattern                                                                             |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Writing task scenarios with product-specific jargon or step-by-step instructions | Use natural language with realistic context and clear goals to test discoverability         |
| Helping users or explaining the UI during test sessions                          | Observe silently and let users struggle; their confusion reveals real issues                |
| Testing only the happy path with ideal inputs                                    | Include error states, edge cases, and recovery scenarios in test plans                      |
| Using fewer than 5 participants per persona                                      | Recruit 5-8 users per persona to reach valid findings per Nielsen's research                |
| Collecting findings without severity scoring or follow-up actions                | Score every issue by impact times frequency and assign fix priority before closing the test |

## Delegation

- **Test plan and scenario creation**: Use `Task` agent to draft objectives, research questions, and realistic task scenarios for each persona
- **Metrics analysis and severity scoring**: Use `Task` agent to calculate SUS scores, task success rates, and severity ratings from raw test data
- **Test infrastructure planning**: Use `Plan` agent to select testing tools, define recruitment criteria, and schedule test waves

## References

- [Test Planning](references/test-planning.md) — objectives, research questions, recruitment, task scenario templates
- [Conducting Tests](references/conducting-tests.md) — think-aloud protocol, facilitation, post-task questions
- [Metrics and Severity](references/metrics-severity.md) — success rate, time on task, errors, satisfaction, SUS scoring, severity formula
- [Reporting](references/reporting.md) — test report template, key insights format, recommended actions structure
- [Remote and Tools](references/remote-and-tools.md) — remote vs in-person comparison, testing tools, test frequency, checklists
