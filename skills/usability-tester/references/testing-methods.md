---
title: Testing Methods
description: Usability testing methods including unmoderated testing, guerrilla testing, first-click testing, cognitive walkthrough, and method selection by product lifecycle stage
tags:
  [
    unmoderated,
    guerrilla,
    first-click,
    cognitive-walkthrough,
    methods,
    lifecycle,
  ]
---

# Testing Methods

## Method Comparison

| Method                | Cost   | Time  | Depth    | Scale          | Best For                             |
| --------------------- | ------ | ----- | -------- | -------------- | ------------------------------------ |
| Moderated testing     | High   | Days  | Deep     | 5-8 users      | Complex flows, new products          |
| Unmoderated testing   | Medium | Hours | Moderate | 20-150 users   | Validation, quantitative data        |
| Guerrilla testing     | Low    | Hours | Shallow  | 5-10 users     | Quick feedback, early concepts       |
| First-click testing   | Low    | Hours | Focused  | 20-50 users    | Navigation, information architecture |
| Cognitive walkthrough | Low    | Hours | Moderate | 2-3 evaluators | Task flow analysis, early design     |
| Card sorting          | Low    | Hours | Focused  | 15-30 users    | Information architecture, labeling   |
| Tree testing          | Low    | Hours | Focused  | 30-50 users    | Navigation structure validation      |

## Unmoderated Testing

Participants complete tasks on their own schedule without a moderator present. Software records their interactions, clicks, and optionally their screen and voice.

### When to Use

- Need quantitative data from a large sample
- Testing straightforward tasks that do not require probing
- Validating findings from moderated testing at scale
- Budget or timeline does not allow moderated sessions

### When NOT to Use

- Testing complex flows that need follow-up questions
- Exploring new product concepts where context matters
- Tasks require domain knowledge that needs explanation
- You need to understand the "why" behind user behavior

### Setup

```yaml
Platform Options:
  - Maze (task-based, integrates with Figma)
  - UserTesting.com (recruit and test, video recording)
  - Lyssna (formerly UsabilityHub, multiple test types)
  - Lookback (asynchronous recording)

Test Configuration:
  - Write clear, unambiguous task instructions
  - Set realistic time limits per task
  - Include a practice task so participants understand the format
  - Add screening questions to filter participants
  - Enable screen recording for qualitative review

Sample Size:
  - Minimum 20 participants for statistical patterns
  - 50+ for quantitative confidence
  - Up to 150 for A/B comparison between designs
```

### Analyzing Unmoderated Results

```yaml
Quantitative Metrics:
  - Task completion rate per task
  - Average time on task
  - Misclick rate (clicks on wrong elements)
  - Drop-off points (where users abandon tasks)

Qualitative Review:
  - Watch recordings of failed tasks to understand why
  - Look for common wrong paths
  - Note where users hesitate (long pauses before clicking)
  - Compare fast completers vs slow completers for pattern differences
```

## Guerrilla Testing

Quick, informal testing with random participants in public places. Sessions last 5-15 minutes and cover 2-3 tasks maximum.

### When to Use

- Very early concept validation
- Testing a single interaction or screen
- Need feedback today, not next week
- Budget is minimal

### When NOT to Use

- Product requires specific domain expertise
- Tasks take more than 5 minutes
- Need consistent, comparable results across sessions
- Testing with a specific persona matters

### How to Run

```yaml
Setup:
  - Prepare a laptop or tablet with the prototype
  - Write 2-3 simple tasks on index cards
  - Choose a high-traffic location (coffee shop, coworking space, campus)
  - Offer a small incentive (coffee, gift card)

Session Flow:
  - Approach: "We're testing a new product. Can I get 5 minutes of your time?"
  - Brief intro: "I'll show you something and ask you to try a couple tasks."
  - Give task card, observe, take notes
  - Quick debrief: 'What was that like? Anything confusing?'
  - Thank and provide incentive

Tips:
  - Keep sessions under 10 minutes
  - Do not explain the product before the task
  - Test the same tasks with each participant for comparison
  - Bring a partner to take notes while you moderate
  - 5-10 participants is enough for guerrilla testing
```

## First-Click Testing

Measures where users click first when given a task. If the first click is correct, users complete the task successfully 87% of the time (based on research by Bob Bailey).

### When to Use

- Evaluating navigation and menu structure
- Testing button placement and labeling
- Comparing two layout options
- Validating information architecture changes

### How to Run

```yaml
Setup:
  - Create a screenshot or static mockup of the page
  - Write task-based questions: 'Where would you click to invite a team member?'
  - Use a tool that records click coordinates (Lyssna, Maze, Optimal Workshop)

Analysis:
  - Generate a click heatmap showing where users clicked
  - Calculate first-click success rate per task
  - Identify competing click targets (multiple areas getting clicks)
  - Compare results across design variations

Success Criteria:
  - 80%+ of users click the correct area on first try: navigation is clear
  - 60-79%: navigation works but could be improved
  - Below 60%: significant navigation or labeling problem
```

## Cognitive Walkthrough

Expert evaluators step through a task flow, asking four questions at each step to identify where users might struggle.

### The Four Questions

At each step in the task flow, the evaluator asks:

```yaml
1. "Will the user try to achieve the right effect?"
Does the user understand what action is needed at this step?

2. "Will the user notice the correct action is available?"
Is the right button, link, or control visible and discoverable?

3. "Will the user associate the correct action with the desired effect?"
Does the label or appearance of the control match what the user expects?

4. "If the correct action is performed, will the user see progress?"
Does the system provide feedback that the action was successful?
```

### How to Run

```yaml
Preparation:
  - Define the target user persona (experience level, goals)
  - List the tasks to evaluate
  - Document the "happy path" steps for each task
  - Gather 2-3 evaluators (can include designers and developers)

Process:
  - Walk through each step of each task
  - At each step, answer all four questions
  - Document any "no" answers as potential usability issues
  - Rate severity of each issue found
  - Compile findings into a prioritized list

Output:
  - List of steps where users are likely to fail or hesitate
  - Specific reasons for each predicted failure
  - Severity ratings for prioritization
  - Recommended fixes for each issue
```

## Card Sorting

Participants organize content items into groups that make sense to them. Reveals how users expect information to be structured.

```yaml
Open Card Sort:
  - Users create their own categories and label them
  - Use for: discovering user mental models, building new IA

Closed Card Sort:
  - Users sort cards into predefined categories
  - Use for: validating an existing or proposed IA

Hybrid Card Sort:
  - Predefined categories plus option to create new ones
  - Use for: refining an IA with known structure

Tools: Optimal Workshop, Maze, UserZoom
Sample Size: 15-30 participants per sort
```

## Tree Testing

Participants navigate a text-based tree structure to find where content lives. Tests the information architecture without visual design influence.

```yaml
Setup:
  - Create a text hierarchy of your site structure
  - Write task-based questions: 'Where would you find the refund policy?'
  - Participants click through the tree to find the answer

Metrics:
  - Task success rate: did they find the right location?
  - Directness: did they go straight there or backtrack?
  - Time to complete: how long did navigation take?

Tools: Optimal Workshop, Treejack, UserZoom
Sample Size: 30-50 participants
```

## Method Selection by Lifecycle Stage

```yaml
Early Concept Stage:
  - Guerrilla testing (quick validation of core concept)
  - Card sorting (information architecture discovery)
  - Cognitive walkthrough (expert review of proposed flows)

Design and Prototyping Stage:
  - Moderated testing (deep insights on task flows)
  - First-click testing (navigation validation)
  - Tree testing (IA validation)
  - Heuristic evaluation (expert review against principles)

Pre-Launch Stage:
  - Unmoderated testing (scale validation, quantitative data)
  - Accessibility testing (inclusive design verification)
  - First-click testing (final navigation check)

Post-Launch Stage:
  - Unmoderated testing (ongoing monitoring)
  - Moderated testing (investigating specific problem areas)
  - Analytics review (complement qualitative findings with data)
```
