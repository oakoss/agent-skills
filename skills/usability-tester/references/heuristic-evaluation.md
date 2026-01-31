---
title: Heuristic Evaluation
description: Nielsen's 10 usability heuristics, evaluation process, severity rating for heuristic issues, and how to combine heuristic evaluation with user testing
tags: [heuristics, nielsen, expert-review, evaluation, ux-audit, severity]
---

# Heuristic Evaluation

Heuristic evaluation is an expert-based inspection method where evaluators examine an interface against established usability principles. It finds approximately 50% of usability issues that user testing would uncover, making it a cost-effective complement to (not replacement for) user testing.

## Nielsen's 10 Usability Heuristics

These 10 principles, developed by Jakob Nielsen, serve as the standard checklist for interface evaluation.

### 1. Visibility of System Status

The system should keep users informed about what is going on through appropriate feedback within a reasonable amount of time.

```yaml
Check For:
  - Loading indicators for operations longer than 1 second
  - Progress bars for multi-step processes
  - Confirmation messages after user actions
  - Clear indication of current location in navigation
  - Real-time validation on form inputs

Common Violations:
  - No feedback after clicking a submit button
  - No indication of upload progress
  - User cannot tell which step they are on in a wizard
  - No visual change when an item is added to a cart
```

### 2. Match Between System and Real World

The system should speak the user's language with familiar words, phrases, and concepts rather than system-oriented terms.

```yaml
Check For:
  - Labels use language the target audience understands
  - Icons match real-world conventions
  - Information appears in a natural and logical order
  - Date formats match locale expectations
  - Error messages use plain language, not error codes

Common Violations:
  - Technical jargon in user-facing labels ("null reference", "404")
  - Unfamiliar abbreviations without explanation
  - Non-standard icons for common actions
  - System-generated IDs shown to users
```

### 3. User Control and Freedom

Users often perform actions by mistake and need a clearly marked exit to leave the unwanted state without going through an extended process.

```yaml
Check For:
  - Undo and redo support for destructive actions
  - Clear cancel buttons on forms and dialogs
  - Back navigation that preserves user input
  - Ability to dismiss modals and overlays easily
  - Confirmation prompts before irreversible actions

Common Violations:
  - No undo after deleting content
  - Modal dialogs with no close button
  - Multi-step form that loses data on back navigation
  - No way to cancel a long-running operation
```

### 4. Consistency and Standards

Users should not have to wonder whether different words, situations, or actions mean the same thing. Follow platform conventions.

```yaml
Check For:
  - Same action uses the same label everywhere
  - Visual design is consistent across pages
  - Interaction patterns match platform conventions
  - Terminology is consistent throughout the product
  - Similar elements behave the same way

Common Violations:
  - "Save" on one page, "Submit" on another for the same action
  - Different button styles for the same action type
  - Inconsistent navigation placement across pages
  - Mixed terminology ("account" vs "profile" for the same thing)
```

### 5. Error Prevention

A design that prevents problems from occurring is better than good error messages.

```yaml
Check For:
  - Constraints that prevent invalid input (date pickers, dropdowns)
  - Confirmation dialogs before destructive actions
  - Inline validation before form submission
  - Sensible defaults that reduce user decisions
  - Disabled states for unavailable actions with explanation

Common Violations:
  - Free text input where a dropdown would prevent errors
  - No confirmation before permanent deletion
  - Validation only after form submission
  - Allowing users to submit incomplete forms
```

### 6. Recognition Rather Than Recall

Minimize the user's memory load by making elements, actions, and options visible. Users should not have to remember information from one part of the interface to another.

```yaml
Check For:
  - Recently used items are easily accessible
  - Labels and instructions are visible, not hidden in tooltips
  - Search suggestions and autocomplete
  - Context preserved when navigating between pages
  - Related information displayed together

Common Violations:
  - User must remember a code from a previous page
  - No recent items or search history
  - Hidden labels that only appear on hover
  - Multi-step process without summary of previous selections
```

### 7. Flexibility and Efficiency of Use

The interface should cater to both novice and expert users. Experienced users should be able to use shortcuts to speed up frequent actions.

```yaml
Check For:
  - Keyboard shortcuts for frequent actions
  - Customizable interface elements
  - Shortcuts and advanced features that do not confuse beginners
  - Bulk actions for repetitive tasks
  - Default values that match common use cases

Common Violations:
  - No keyboard shortcuts for power users
  - No bulk selection or batch operations
  - Forced multi-step wizards with no quick path for experts
  - Settings that require multiple clicks to reach frequently
```

### 8. Aesthetic and Minimalist Design

Every extra unit of information competes with relevant information and diminishes its relative visibility.

```yaml
Check For:
  - Content hierarchy prioritizes important information
  - Minimal use of decorative elements that do not aid comprehension
  - White space used effectively to reduce visual noise
  - Only essential information shown by default, details on demand
  - Visual design supports rather than competes with content

Common Violations:
  - Cluttered dashboards showing everything at once
  - Decorative animations that slow down task completion
  - Dense text without visual hierarchy
  - Too many competing calls to action on one page
```

### 9. Help Users Recognize, Diagnose, and Recover from Errors

Error messages should be expressed in plain language, precisely indicate the problem, and constructively suggest a solution.

```yaml
Check For:
  - Error messages explain what went wrong in plain language
  - Error messages suggest how to fix the problem
  - Errors are displayed near the relevant input field
  - Error state is visually distinct (color, icon, position)
  - Users can fix errors without re-entering all data

Common Violations:
  - Generic "Something went wrong" with no details
  - Error codes instead of human-readable messages
  - Error message at top of page, far from the problematic field
  - Form clears all fields after a validation error
```

### 10. Help and Documentation

The interface should provide help and documentation that is easy to search, focused on the user's task, and concise.

```yaml
Check For:
  - Contextual help available where users need it
  - Searchable help documentation
  - Onboarding or guided tours for new users
  - Tooltips for complex or unfamiliar features
  - FAQ or knowledge base for common questions

Common Violations:
  - No in-app help or documentation
  - Help content that does not match the current product version
  - Documentation that requires leaving the application
  - No onboarding for new users
```

## Running a Heuristic Evaluation

```yaml
Process: 1. Select 3-5 evaluators (mix of UX expertise and domain knowledge)
  2. Brief evaluators on the product, target users, and key tasks
  3. Each evaluator independently inspects the interface
  4. Each evaluator documents issues with heuristic violated and severity
  5. Compile all findings, removing duplicates
  6. Prioritize by severity and frequency across evaluators
  7. Present findings to the team with recommendations

Time Estimate:
  - Individual evaluation: 1-2 hours per evaluator
  - Compilation and debrief: 2-3 hours
  - Total: 1-2 days for a complete evaluation

Tips:
  - Evaluators should work independently to avoid groupthink
  - Walk through key user tasks, not just browse the interface
  - Document the specific location and context of each issue
  - Take screenshots to illustrate issues
  - Rate severity independently before comparing with other evaluators
```

## Severity Rating for Heuristic Issues

```yaml
0 - Not a usability problem: Cosmetic only, no impact on task completion

1 - Cosmetic problem: Fix if time permits, does not affect usability

2 - Minor usability problem: Low priority, causes slight delay or confusion

3 - Major usability problem: High priority, causes significant difficulty for users

4 - Usability catastrophe: Must fix before release, prevents task completion
```

## Combining with User Testing

Heuristic evaluation and user testing are complementary methods that find different types of issues.

```yaml
Recommended Order: 1. Run heuristic evaluation first (cheaper, faster)
  2. Fix critical and major issues found
  3. Then run user testing to find issues experts missed
  4. Focus user testing time on areas heuristic evaluation flagged as uncertain

What Heuristic Evaluation Finds Better:
  - Consistency violations across the interface
  - Missing standard features (undo, error messages)
  - Accessibility violations
  - Platform convention deviations

What User Testing Finds Better:
  - Mental model mismatches
  - Terminology confusion
  - Task flow problems
  - Unexpected user strategies
  - Emotional responses to design decisions
```
