---
title: Conducting Tests
description: Think-aloud protocol instructions, facilitation rules, note-taking framework, post-task interview questions, and session management for moderated usability testing
tags:
  [
    think-aloud,
    facilitation,
    interview,
    protocol,
    observation,
    note-taking,
    moderation,
  ]
---

# Conducting Tests

## Think-Aloud Protocol

The think-aloud protocol is the primary method for understanding user mental models during testing. There are two variants.

### Concurrent Think-Aloud

The participant verbalizes thoughts while performing tasks. Use for most moderated tests.

Key instruction to participant:

```text
"Please think aloud as you work. Tell me what you're looking for,
what you're thinking, what you're trying to do. There are no
wrong answers -- we're testing the product, not you."
```

If the participant goes silent for more than 10-15 seconds:

```text
"What are you thinking right now?"
"What are you looking for?"
"Tell me what's going through your mind."
```

### Retrospective Think-Aloud

The participant completes the task silently, then reviews a recording and explains their thought process. Use when concurrent verbalization would interfere with the task (timing-sensitive interactions, complex calculations).

```text
"Now let's watch the recording together. Please tell me what you
were thinking at each point. I'll pause if you want to explain
something in more detail."
```

## What to Listen For

| Verbal Cue                     | What It Reveals                                 | Action                           |
| ------------------------------ | ----------------------------------------------- | -------------------------------- |
| "I'm looking for..."           | User expectations about where things should be  | Note expected vs actual location |
| "I thought this would..."      | Mental model mismatch with system model         | Document the gap                 |
| "This is confusing because..." | Specific friction point with articulated reason | Capture verbatim                 |
| "I'm not sure if..."           | Uncertainty, lack of confidence in action       | Note what caused hesitation      |
| "Oh, I see..."                 | Recovery moment after confusion                 | Note what finally made it clear  |
| "Wait, what happened?"         | Unexpected system behavior                      | Note the trigger and response    |
| Long silence                   | Participant is stuck or confused                | Prompt gently after 15 seconds   |

## Facilitation Rules

### Do

- Observe silently while the participant works
- Take timestamped notes on behavior, not just outcomes
- Let them struggle -- this reveals real discoverability issues
- Ask follow-up questions AFTER each task, not during
- Stay physically neutral (no nodding, no frowning)
- Use the "echo" technique: repeat their words back as a question
- Redirect if they ask you a question: "What would you do if I weren't here?"

### Do Not

- Help or explain the interface
- Lead them ("maybe try clicking the menu...")
- Defend design choices ("that's because we designed it to...")
- Interrupt during a task
- Show frustration, surprise, or disappointment
- Answer questions about the interface during tasks
- Rush participants who are taking longer than expected

## The Echo Technique

When participants ask questions or make statements, reflect them back instead of answering.

```yaml
Participant: "Should I click this button?"
Moderator: "What do you think that button does?"

Participant: "Is this the right page?"
Moderator: "What were you expecting to see?"

Participant: "I don't know what to do next."
Moderator: "What would you try if I weren't here?"

Participant: "This doesn't make sense."
Moderator: "Tell me more about what doesn't make sense."
```

## Note-Taking Framework

Use a structured format to capture observations consistently across sessions.

```yaml
Note Template:
  Timestamp: [MM:SS from session start]
  Task: [Which task number]
  Observation Type: [action | verbalization | error | recovery | abandonment]
  Description: [What happened]
  Participant Quote: [Verbatim if notable]
  Severity Estimate: [low | medium | high | critical]

Example Notes:
  - "02:15 | Task 2 | action | Clicked 'Settings' looking for invite feature"
  - "02:30 | Task 2 | verbalization | 'I expected invite to be on the project page'"
  - '03:00 | Task 2 | error | Opened wrong menu, had to backtrack'
  - '03:45 | Task 2 | recovery | Found invite in team settings after browsing'
```

## Post-Task Questions

Ask these immediately after each task while the experience is fresh.

```yaml
Completion Questions:
  - 'On a scale of 1-5, how easy was that task?'
  - 'What were you expecting to see?'
  - 'What was confusing about that process?'
  - 'If you could change one thing about that experience, what would it be?'

Discovery Questions:
  - 'Where did you expect to find that feature?'
  - 'What do you think this [element] does?'
  - 'Why did you click there first?'
  - 'Was there a point where you felt lost?'

Comparison Questions (for redesigns):
  - 'How does this compare to how you usually do this task?'
  - 'Was anything easier or harder than you expected?'
```

## Post-Session Questions

Ask at the end of all tasks for overall impressions.

```yaml
Overall Experience:
  - 'What was the most frustrating part of your experience?'
  - 'What was the easiest part?'
  - 'If you were describing this product to a friend, what would you say?'
  - 'Would you use this product? Why or why not?'
  - 'Is there anything else you want to share about your experience?'

Feature Prioritization:
  - 'If you could add one feature, what would it be?'
  - "Was there anything you expected to find but didn't?"
```

## Session Management

### When to Intervene

Intervention should be rare but sometimes necessary.

```yaml
Intervene When:
  - Participant is visibly distressed (not just frustrated)
  - Participant has been stuck for more than the time limit
  - Technical failure prevents task completion (bug, crash)
  - Participant explicitly asks to stop

Do Not Intervene When:
  - Participant is frustrated but still trying
  - Participant is taking a wrong path (this is valuable data)
  - Participant pauses to think
  - Participant makes an error they can recover from
```

### Handling Common Situations

```yaml
Participant asks for help:
  Response: "What would you do if I weren't here?"
  If stuck beyond time limit: "Let's move on to the next task."

Participant gets emotional:
  Response: "Remember, we're testing the product, not you. It's completely
  fine to find things difficult -- that's exactly why we're testing."

Participant wants to quit a task:
  Response: "That's fine, let's move on. Can you tell me what you found
  difficult about that?"

Technical failure:
  Response: Note the failure, skip the task, move on. Do not debug
  during the session.
```

## Between-Session Checklist

```yaml
After Each Session:
  - Save and label the recording
  - Review notes while memory is fresh
  - Flag top 3 issues observed
  - Note any changes needed to the test script
  - Reset the test environment to starting state
  - Take a 10-minute break before the next session
```
