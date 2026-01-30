---
paths:
  - 'skills/**/references/*accessibility*.md'
  - 'skills/**/references/*aria*.md'
  - 'skills/**/references/*focus*.md'
  - 'skills/**/references/*forms*.md'
---

# Accessibility Rules (jsx-a11y recommended)

All these are enforced - violations will cause lint errors.

Custom components mapped: `Button`→button, `Input`→input, `Select`→select

## Images & Media

- `alt-text` - Images must have meaningful alt text
- `img-redundant-alt` - Alt text cannot contain "image", "picture", or "photo"
- `media-has-caption` - Audio/video must have captions track
- `iframe-has-title` - Iframes must have title attribute

## Links & Buttons

- `anchor-has-content` - Links must have accessible content
- `anchor-is-valid` - Links must be valid navigable elements
- `heading-has-content` - Headings must have accessible content

## Keyboard Accessibility

- `click-events-have-key-events` - Clickable elements need keyboard handlers
- `mouse-events-have-key-events` - onMouseOver/Out need onFocus/Blur
- `interactive-supports-focus` - Interactive elements must be focusable
- `tabindex-no-positive` - tabIndex must not be > 0
- `no-noninteractive-tabindex` - tabIndex only on interactive elements (exception: `role="region"` or `role="tabpanel"` for scrollable areas)
- `no-autofocus` - Don't use autoFocus prop

## ARIA

- `aria-props` - All aria-\* props must be valid
- `aria-proptypes` - ARIA values must be valid
- `aria-role` - ARIA roles must be valid, non-abstract
- `role-has-required-aria-props` - Roles must have required attributes
- `role-supports-aria-props` - Only use aria-\* supported by role
- `aria-activedescendant-has-tabindex` - aria-activedescendant needs tabindex
- `aria-unsupported-elements` - Don't add ARIA to unsupported elements

## Roles & Semantics

- `no-redundant-roles` - Don't set role same as implicit role
- `no-interactive-element-to-noninteractive-role` - Don't downgrade interactive elements
- `no-noninteractive-element-to-interactive-role` - Don't upgrade non-interactive elements
- `no-noninteractive-element-interactions` - No click handlers on non-interactive elements
- `no-static-element-interactions` - Static elements with handlers need role
- `no-distracting-elements` - No `<marquee>` or `<blink>`

## Forms

- `label-has-associated-control` - Labels must have associated control
- `autocomplete-valid` - Autocomplete values must be valid

## Document

- `html-has-lang` - `<html>` must have lang attribute
- `scope` - scope prop only on `<th>` elements

## Code Examples

### Buttons with Icons

```tsx
// Bad - no accessible label
<Button size="icon">
  <MenuIcon />
</Button>

// Good - has aria-label
<Button size="icon" aria-label="Open menu">
  <MenuIcon />
</Button>

// Good - has visible text
<Button>
  <MenuIcon />
  <span>Menu</span>
</Button>
```

### Form Labels

```tsx
// Bad - no label association
<Input placeholder="Email" />

// Good - label with htmlFor
<Label htmlFor="email">Email</Label>
<Input id="email" />

// Good - aria-label for icon inputs
<Input aria-label="Search" placeholder="Search..." />
```

### Images

```tsx
// Bad - empty alt
<img src="/hero.jpg" alt="" />

// Bad - redundant alt
<img src="/hero.jpg" alt="Image of hero section" />

// Good - meaningful alt
<img src="/hero.jpg" alt="Team collaborating in modern office" />

// Good - decorative image (explicitly empty)
<img src="/decoration.svg" alt="" role="presentation" />
```

### Interactive Elements

```tsx
// Bad - div with click handler
<div onClick={handleClick}>Click me</div>

// Good - use button
<button onClick={handleClick}>Click me</button>

// Good - if div needed, add role and keyboard
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  Click me
</div>
```

### Focus Management

```tsx
// Bad - positive tabIndex
<Button tabIndex={5}>Submit</Button>

// Good - natural tab order
<Button>Submit</Button>

// Good - remove from tab order when needed
<Button tabIndex={-1}>Hidden from tab</Button>
```
