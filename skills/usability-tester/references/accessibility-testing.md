---
title: Accessibility Testing
description: Inclusive usability testing with participants with disabilities, assistive technology testing, WCAG alignment, and accessibility-specific heuristics
tags:
  [
    accessibility,
    wcag,
    assistive-technology,
    screen-reader,
    inclusive-design,
    disabilities,
  ]
---

# Accessibility Testing

Accessibility testing validates that people with disabilities can use the product effectively. It combines automated checks, expert review against WCAG guidelines, and usability testing with participants who use assistive technologies.

## When to Test for Accessibility

```yaml
Pre-Launch (required):
  - Run automated accessibility scanner (catches ~30% of issues)
  - Conduct expert WCAG audit against Level AA criteria
  - Test with screen reader on key user flows
  - Test keyboard-only navigation on all interactive elements

Post-Launch (recommended):
  - Usability test with 3-5 participants with disabilities
  - Test new features with assistive technologies before release
  - Quarterly accessibility audit of high-traffic pages

Compliance Checkpoints:
  - Before any public-facing release
  - When adding new interactive components
  - When redesigning navigation or forms
  - When changing color schemes or typography
```

## Inclusive Recruitment

Recruit participants with disabilities who represent your actual user base.

```yaml
Participant Mix (minimum 3-5 participants):
  - At least 1 screen reader user (JAWS, NVDA, or VoiceOver)
  - At least 1 keyboard-only user (motor impairment)
  - At least 1 user with low vision (magnification, high contrast)
  - Consider: cognitive disabilities, hearing impairments (for video/audio content)

Recruitment Sources:
  - Disability advocacy organizations
  - Specialized recruitment panels (Fable, AbilityNet)
  - University disability services
  - Existing user base (add accessibility questions to screener)

Screening Considerations:
  - Ask about assistive technology used daily (not just occasionally)
  - Ask about experience level with the assistive technology
  - Confirm the participant's setup matches the test environment
  - Schedule extra time (sessions may run 25-50% longer)

Incentives:
  - Pay at least the same rate as other participants (never less)
  - Offer flexible scheduling (transportation may take longer)
  - For remote tests: verify the participant's setup supports screen sharing
```

## Test Adaptations

Usability tests with participants with disabilities require protocol modifications.

```yaml
Session Adjustments:
  - Allow 75-90 minutes instead of 60 (tasks take longer with AT)
  - Reduce to 3-4 tasks instead of 5
  - Provide task instructions in multiple formats (verbal, written, large print)
  - Be prepared for the session to run at a different pace
  - Have backup plans if the participant's AT has compatibility issues

Think-Aloud Modifications:
  - Screen reader users may find concurrent think-aloud harder (AT already produces audio)
  - Consider retrospective think-aloud for screen reader users
  - Ask screen reader users to describe what they hear, not just what they do
  - For keyboard users: ask them to describe their navigation strategy

Facilitation Notes:
  - Do not assume what the participant can or cannot do
  - Let the participant use their own device and AT setup when possible
  - Ask how they normally approach similar tasks before starting
  - If using remote testing, test the screen sharing setup in advance
  - Describe any visual elements if the participant cannot see them
```

## Assistive Technology Testing

Even without users with disabilities, the team should test with assistive technologies directly.

### Screen Reader Testing

```yaml
Test With:
  - VoiceOver (macOS/iOS, built-in)
  - NVDA (Windows, free)
  - JAWS (Windows, enterprise standard)

Key Checks:
  - All interactive elements are reachable and labeled
  - Images have meaningful alt text (or empty alt for decorative)
  - Form fields have associated labels
  - Error messages are announced when they appear
  - Page structure uses proper heading hierarchy (h1 through h6)
  - Dynamic content updates are announced (ARIA live regions)
  - Modal dialogs trap focus correctly
  - Tables have proper headers for data relationships

Common Issues Found:
  - Unlabeled buttons (icon-only with no accessible name)
  - Custom components not announcing their role or state
  - Focus moves to unexpected locations after interactions
  - Dynamic content changes silently (no announcement)
```

### Keyboard Navigation Testing

```yaml
Test All Pages For:
  - Every interactive element reachable via Tab key
  - Logical tab order (left-to-right, top-to-bottom)
  - Visible focus indicator on every focusable element
  - Escape key closes modals and dropdowns
  - Enter or Space activates buttons and links
  - Arrow keys navigate within components (menus, tabs, radio groups)
  - No keyboard traps (focus gets stuck in a component)
  - Skip navigation link available to bypass repeated content

Common Issues Found:
  - Custom dropdowns not keyboard accessible
  - Focus indicator hidden by CSS (outline: none without replacement)
  - Tab order jumps around the page illogically
  - Modal does not return focus to trigger element on close
```

### Visual Testing

```yaml
Color Contrast:
  - Normal text: 4.5:1 contrast ratio minimum (WCAG AA)
  - Large text (18px+ or 14px+ bold): 3:1 contrast ratio minimum
  - UI components and graphical objects: 3:1 contrast ratio minimum
  - Check with browser DevTools or contrast checker tools

Zoom and Magnification:
  - Content remains usable at 200% browser zoom
  - No horizontal scrolling at 200% zoom on standard viewports
  - Text resizes properly without breaking layout
  - Touch targets remain accessible when zoomed

Color Independence:
  - Information is not conveyed by color alone
  - Error states use icons or text in addition to red color
  - Charts and graphs have patterns or labels, not just colors
  - Links are distinguishable from surrounding text without color
```

## Accessibility Heuristics

Five principles for evaluating accessibility, complementing Nielsen's general usability heuristics.

```yaml
1. Perceivable:
  - All content available in text or text alternatives
  - Captions for video, transcripts for audio
  - Content adaptable to different presentations (reflow, zoom)
  - Sufficient contrast for all text and UI components

2. Operable:
  - All functionality available via keyboard
  - Users have enough time to read and interact
  - No content that flashes more than 3 times per second
  - Multiple ways to navigate (search, sitemap, breadcrumbs)

3. Understandable:
  - Text is readable and comprehensible
  - Pages behave predictably (no unexpected changes)
  - Users can avoid and correct mistakes
  - Instructions do not rely solely on sensory characteristics

4. Robust:
  - Content works with current and future assistive technologies
  - Valid HTML with proper ARIA attributes
  - Custom components follow WAI-ARIA authoring practices
  - Compatible across browsers and devices

5. Inclusive Interaction:
  - Multiple input methods supported (mouse, keyboard, touch, voice)
  - Error recovery is accessible to all users
  - Help and documentation accessible with assistive technology
  - Timeout warnings give users enough time to respond
```

## WCAG Quick Reference

Focus on the most commonly violated criteria.

```yaml
Most Frequently Failed WCAG AA Criteria:
  - 1.1.1 Non-text Content (missing alt text)
  - 1.3.1 Info and Relationships (missing form labels, heading structure)
  - 1.4.3 Contrast Minimum (text below 4.5:1 ratio)
  - 2.1.1 Keyboard (interactive elements not keyboard accessible)
  - 2.4.4 Link Purpose (generic "click here" or "read more" links)
  - 3.3.2 Labels or Instructions (form fields without labels)
  - 4.1.2 Name, Role, Value (custom components without ARIA)

Automated Tools (catch ~30% of issues):
  - axe DevTools (browser extension, free)
  - WAVE (browser extension, free)
  - Lighthouse (built into Chrome DevTools)
  - pa11y (command line, CI integration)

Manual Checks Required For:
  - Logical reading order
  - Meaningful alt text quality
  - Keyboard focus management
  - ARIA implementation correctness
  - Cognitive load and readability
```

## Reporting Accessibility Findings

```yaml
Issue Format:
  Title: [Short description]
  WCAG Criterion: [e.g., 1.4.3 Contrast Minimum]
  Level: [A | AA | AAA]
  Severity: [Critical | High | Medium | Low]
  Affected Users: [Which disability groups]
  Location: [Page and component]
  Current Behavior: [What happens now]
  Expected Behavior: [What should happen]
  Remediation: [Specific fix with code example if relevant]

Example:
  Title: Search button has no accessible name
  WCAG Criterion: 4.1.2 Name, Role, Value
  Level: A
  Severity: Critical
  Affected Users: Screen reader users
  Location: Global header, search component
  Current Behavior: Screen reader announces "button" with no label
  Expected Behavior: Screen reader announces "Search button"
  Remediation: Add aria-label="Search" to the button element
```
