---
title: Reporting
description: Usability test report template with participant profiles, task results, issue tracking, SUS scores, key insights, and recommended actions
tags: [reporting, template, insights, recommendations, test-report]
---

# Reporting

## Test Report Template

```yaml
usability_test_summary:
  date: '2024-01-20'
  participants: 8
  participant_profile: 'New users, age 25-45, tech-savvy'

  tasks:
    - task: 'Create a new project'
      success_rate: '87.5% (7/8)'
      avg_time: '1m 24s'
      errors: 1.2 per user
      satisfaction: 4.3/5

    - task: 'Invite team member'
      success_rate: '62.5% (5/8)'
      avg_time: '2m 45s'
      errors: 2.8 per user
      satisfaction: 3.1/5

  issues:
    - issue: "Users can't find 'Invite' button"
      severity: high
      impact: 3
      frequency: 3
      affected_users: 7/8
      recommendation: "Move 'Invite' button to top of project page, make it more prominent"

    - issue: 'Confusion about project vs workspace'
      severity: medium
      impact: 2
      frequency: 3
      affected_users: 6/8
      recommendation: 'Add tooltip explaining difference, update onboarding'

    - issue: 'Export button text unclear'
      severity: low
      impact: 1
      frequency: 2
      affected_users: 2/8
      recommendation: "Change 'Export' to 'Export to CSV'"

  sus_score: 72 (Good)

  key_insights:
    - 'Onboarding is smooth (87.5% success)'
    - 'Team collaboration features hard to discover'
    - 'Overall product easy to use once features are found'

  recommended_actions:
    1. "High priority: Redesign invite flow"
    2. "Medium priority: Add contextual help for workspace vs project"
    3. "Low priority: Update button labels"
```
