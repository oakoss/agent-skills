---
title: Design Process
description: 5-phase UX design process covering information architecture, user flows, wireframing, prototyping and testing, and UI design handoff
tags:
  [
    design-process,
    information-architecture,
    user-flows,
    wireframing,
    prototyping,
    handoff,
  ]
---

# Design Process

## Phase 1: Information Architecture

**Goal:** Organize content and functionality logically.

**Activities:**

- **Card sorting** -- let users organize content into categories to discover their mental models
- **Site mapping** -- create hierarchy of pages and features
- **Navigation design** -- define primary, secondary, and utility navigation structures
- **Labeling** -- establish clear, user-friendly terminology that matches user expectations

**Validation checklist:**

- IA tested with 5+ users via tree testing
- Navigation paths are clear and logical
- Labels match user mental models (not internal jargon)

## Phase 2: User Flows

**Goal:** Map paths users take to complete tasks.

**Key flows to design:**

- **Onboarding** -- first-time user experience from signup to first value
- **Core tasks** -- primary use cases covering 80% of usage
- **Error states** -- recovery paths from mistakes
- **Edge cases** -- less common but important scenarios

**Flow diagram elements:**

```text
[Entry Point] --> [Decision] --> [Action] --> [Outcome]
                       |
                  [Alternative Path]
```

**Validation checklist:**

- Happy path documented for each core task
- Error states designed with clear recovery actions
- Exit points identified at each step
- Flows validated against user research data

## Phase 3: Wireframing

**Goal:** Create low-fidelity layouts focusing on structure over visual design.

**Fidelity levels:**

| Level   | Characteristics                                  | When to Use                       |
| ------- | ------------------------------------------------ | --------------------------------- |
| Low-fi  | Sketches, boxes, placeholder text                | Early exploration, fast iteration |
| Mid-fi  | Grayscale, realistic content, basic interactions | Stakeholder review, user testing  |
| High-fi | Styled, branded, detailed interactions           | Final approval, developer handoff |

**Key screens to wireframe:**

- Homepage or dashboard
- Core task screens (CRUD operations)
- Navigation (header, sidebar, footer)
- Forms and input validation states
- Empty states, loading states, error states

**Wireframe checklist:**

- Clear visual hierarchy (size, weight, contrast)
- Consistent layout patterns across screens
- Accessible contrast and sizing
- Touch targets at least 44x44px on mobile
- Forms grouped logically with clear labels

## Phase 4: Prototyping and Testing

**Goal:** Create interactive prototypes for usability testing.

**Prototyping tools:**

- **Figma** (recommended) -- collaborative, browser-based, built-in prototyping
- **Framer** -- code-based prototyping for advanced interactions
- **ProtoPie** -- complex micro-interactions and multi-device prototypes

**Usability testing script:**

```text
1. Welcome (5 min): Explain process, get consent, set expectations
2. Context (5 min): Ask about current solutions, pain points
3. Tasks (20 min): "Try to [complete specific task]"
4. Think-aloud: "Tell me what you are thinking as you work"
5. Debrief (5 min): Overall impressions, suggestions
```

**Usability metrics:**

| Metric               | Target | How to Measure                  |
| -------------------- | ------ | ------------------------------- |
| Task completion rate | >70%   | Users who complete successfully |
| Time on task         | Varies | Stopwatch per task              |
| Error rate           | <20%   | Wrong paths or backtracking     |
| Satisfaction score   | >3.5/5 | Post-test questionnaire         |

**Validation checklist:**

- Prototype covers all main user flows
- 5+ users tested (catches ~85% of issues)
- Task completion rate exceeds 70%
- Critical issues documented and addressed

## Phase 5: UI Design and Handoff

**Goal:** Create high-fidelity, production-ready designs.

**Design system elements:**

- **Colors** -- primary, secondary, neutrals, semantic (error, success, warning, info)
- **Typography** -- scale (h1-h6, body, small), weights, line heights
- **Spacing** -- 4pt or 8pt grid system for consistent rhythm
- **Components** -- buttons, inputs, cards, modals, tooltips, dropdowns
- **Icons** -- consistent set (Heroicons, Lucide, or Font Awesome)

**Component states to design:**

| State    | Description                           |
| -------- | ------------------------------------- |
| Default  | Normal resting state                  |
| Hover    | Mouse cursor over the element         |
| Active   | Element being clicked or pressed      |
| Focused  | Element selected via keyboard         |
| Disabled | Element not available for interaction |
| Error    | Validation failed or error occurred   |
| Loading  | Action in progress                    |

**Developer handoff deliverables:**

- Design specs (spacing, colors, fonts) via inspect mode
- Component states documented (default, hover, active, disabled, error)
- Responsive breakpoints for mobile, tablet, and desktop
- Interaction specifications (animations, transitions, micro-interactions)
- Exported assets (icons, images, logos in required formats)

**Handoff checklist:**

- Designs match brand guidelines
- Accessibility verified (contrast, keyboard navigation)
- Responsive layouts defined for all breakpoints
- Component library documented with usage guidelines
- Handoff reviewed with development team
