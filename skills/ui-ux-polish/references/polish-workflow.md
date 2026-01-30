---
title: Polish Workflow
description: The iterative UI/UX polish prompt, why it works, single and multi-agent iteration protocols, what the model typically improves, and when to use versus skip
tags: [polish, iterative, workflow, prompt, desktop, mobile, Stripe]
---

## The Polish Prompt

This prompt drives iterative visual refinement. Run it repeatedly (10+ times) for compounding improvements:

```text
I still think there are strong opportunities to enhance the UI/UX look and feel and to make everything work better and be more intuitive, user-friendly, visually appealing, polished, slick, and world class in terms of following UI/UX best practices like those used by Stripe, don't you agree? And I want you to carefully consider desktop UI/UX and mobile UI/UX separately while doing this and hyper-optimize for both separately to play to the specifics of each modality. I'm looking for true world-class visual appeal, polish, slickness, etc. that makes people gasp at how stunning and perfect it is in every way. Use ultrathink.
```

### Alternative: General Scrutiny

```text
Great, now I want you to super carefully scrutinize every aspect of the application workflow and implementation and look for things that just seem sub-optimal or even wrong/mistaken to you, things that could very obviously be improved from a user-friendliness and intuitiveness standpoint, places where our UI/UX could be improved and polished to be slicker, more visually appealing, and more premium feeling and just ultra high quality, like Stripe-level apps.
```

## Why This Prompt Works

### Asks for Agreement

The phrase "don't you agree?" engages the model's reasoning about whether improvements are possible, rather than just executing instructions.

### Separates Desktop and Mobile

Explicitly requesting separate optimization for each modality prevents compromises that work "okay" on both but great on neither.

### Sets High Standards

References to "world class", "best practices like Stripe", and "makes people gasp" anchor the model toward higher quality than generic "make it better" instructions.

### Uses Extended Thinking

Extended thinking allows the model to analyze the current state thoroughly, consider multiple improvement options, and choose the highest-impact changes.

## Iteration Protocol

### Single Agent

1. Run the polish prompt
2. Review the changes the agent makes
3. Run the same prompt again
4. Repeat 10+ times until changes become minimal

Each pass adds incremental improvements that compound. An app after 10 passes looks dramatically better than after 1 pass.

### Multiple Agents

Multiple agents can work on UI/UX polish simultaneously:

- They focus on different areas of the application
- Use file reservations to avoid conflicts
- Compound improvements faster

## What the Model Typically Improves

### Visual Polish

- Spacing and padding consistency
- Typography hierarchy
- Color contrast and accessibility
- Shadow and depth effects
- Border radius consistency
- Hover and focus states

### Interaction Design

- Button feedback
- Loading states
- Transitions and animations
- Error state handling
- Empty state design

### Mobile Optimization

- Touch target sizes (minimum 44x44px)
- Responsive breakpoints
- Mobile-specific navigation
- Gesture support
- Performance on mobile devices

### Desktop Optimization

- Keyboard navigation
- Hover states
- Multi-column layouts
- Sidebar navigation
- Power user shortcuts

## Prerequisites

Before running the polish workflow, ensure:

- App works correctly (no functional bugs)
- Basic styling is in place
- A design system or component library exists
- Ready for iterative refinement

If the app needs a complete overhaul, establish a design system and component library first.
