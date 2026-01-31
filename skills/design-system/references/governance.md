---
title: Governance
description: Semantic versioning for design systems, deprecation strategy, contribution workflow, component lifecycle prioritization, and changelog management
tags:
  [
    governance,
    versioning,
    semver,
    deprecation,
    changelog,
    contribution,
    lifecycle,
  ]
---

# Governance

Design systems require clear governance to scale across teams. This covers versioning, deprecation, contribution processes, and component prioritization.

## Semantic Versioning

Treat token and component changes as API changes. Follow semver strictly.

| Change Type | Version Bump | Examples                                      |
| ----------- | ------------ | --------------------------------------------- |
| Breaking    | Major        | Removed prop, renamed token, changed defaults |
| New feature | Minor        | New component, new variant, new token         |
| Bug fix     | Patch        | CSS fix, a11y fix, TypeScript correction      |

### What Counts as Breaking

- Removing or renaming a component prop
- Changing a prop's type signature
- Removing or renaming a design token
- Changing default behavior (a previously-optional prop becomes required)
- Changing the DOM structure components render

### What Does Not Break

- Adding new optional props
- Adding new components
- Adding new token values
- Bug fixes that match documented behavior
- Accessibility improvements

## Deprecation Strategy

Deprecate gradually across three releases before removing.

### Step 1: Announce Deprecation

```ts
interface ButtonProps {
  /** @deprecated Use `variant` instead. Will be removed in v3.0.0. */
  type?: 'primary' | 'secondary';
  variant?: 'primary' | 'secondary';
}
```

### Step 2: Support Both with Runtime Warning

```ts
function Button({ type, variant, ...props }: ButtonProps) {
  if (type && process.env.NODE_ENV === 'development') {
    console.warn(
      'Button: `type` prop is deprecated. Use `variant` instead. Removal in v3.0.0.',
    );
  }
  const resolved = variant ?? type ?? 'primary';
  return <button data-variant={resolved} {...props} />;
}
```

### Step 3: Remove in Next Major

```ts
interface ButtonProps {
  variant?: 'primary' | 'secondary';
}
```

Document the migration path in the changelog.

## Contribution Workflow

```text
1. Proposal    -> GitHub issue with use case and API sketch
2. Design      -> Figma mockup reviewed by design lead
3. API review  -> TypeScript interface approved before coding
4. Build       -> PR with implementation, tests, and stories
5. Document    -> Storybook docs with usage guidelines
6. Release     -> Semver bump + changelog entry
```

### Proposal Template

Proposals should answer:

- **Problem**: What user need does this solve?
- **Usage**: When should this component/token be used?
- **API**: What does the TypeScript interface look like?
- **Accessibility**: How will it be keyboard and screen reader accessible?
- **Alternatives**: What other approaches were considered?

## Component Lifecycle

Prioritize components by product need:

| Priority | Components                                     | Criteria                   |
| -------- | ---------------------------------------------- | -------------------------- |
| P0       | Button, Input, Label, Text, Icon, FormField    | Used on every screen       |
| P1       | Select, Checkbox, Radio, Switch, Tabs, Tooltip | Used in most forms/layouts |
| P2       | DatePicker, Combobox, Slider, Toast, Drawer    | Used in specific features  |
| P3       | DataTable, Calendar, FileUpload, Stepper       | Complex, domain-specific   |

Build P0 first, then ship P1 once P0 is stable. P2 and P3 are added based on product demand.

## Changelog Management

Maintain a changelog that documents every release. Use tools like Changesets for automated changelog generation in monorepos.

### Changelog Format

```markdown
## [2.0.0]

### Breaking Changes

- **Button**: Renamed `type` prop to `variant`
- **tokens**: Removed `color-gray-500` (use `color-gray-600`)

### Migration Guide

Replace `type` with `variant` on all Button instances:

- Before: `<Button type="primary">`
- After: `<Button variant="primary">`

## [1.5.0]

### Added

- **Toast**: New component for notifications
- **Button**: New `isLoading` prop

### Fixed

- **Button**: Focus outline visible on all browsers
- **Input**: Placeholder color meets WCAG contrast
```

## Design System Team Roles

| Role         | Responsibility                                  |
| ------------ | ----------------------------------------------- |
| Owner        | Vision, roadmap, final approval                 |
| Design lead  | Visual standards, Figma library, design review  |
| Engineering  | Implementation, tooling, CI/CD, releases        |
| Contributors | Product teams proposing and building components |

## Token Governance

Tokens are shared infrastructure. Changes require the same review rigor as API changes.

- New primitive tokens need justification (does a similar value exist?)
- Semantic tokens must map to documented use cases
- Component tokens are scoped to a single component
- Unused tokens are removed during quarterly audits
- Token naming follows the established convention (kebab-case, category-purpose pattern)

## Quality Gates

Before any release, verify:

- All components pass automated a11y tests (jest-axe)
- Visual regression tests show no unintended changes (Chromatic)
- TypeScript types are correct and exported
- Storybook stories exist for all variants and states
- Changelog entry describes the change
- Token changes are backward-compatible (or major version bumped)
