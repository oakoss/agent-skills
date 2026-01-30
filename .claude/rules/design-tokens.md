---
paths:
  - 'skills/**/references/*design-tokens*.md'
  - 'skills/**/references/*theming*.md'
  - 'skills/**/references/*color*.md'
---

# Design Tokens & Semantic Color System

Rules for managing CSS custom properties and design tokens in the UI package theme.

## Token Architecture (2-Tier System)

We follow a 2-tier token architecture, intentionally avoiding component-specific tokens:

```text
Layer 1: Primitives    → Raw values (internal, not exposed)
Layer 2: Semantic      → Context-aware, purpose-driven (public API)
```

**Why 2-tier instead of 3-tier?**

- Component tokens create maintenance burden without proportional value
- Semantic tokens provide enough abstraction for theming
- Simpler to maintain and understand

### Layer 1: Primitive Tokens

Raw values with no context. These define WHAT options exist:

```css
--blue-100: oklch(0.97 0.02 255);
--blue-500: oklch(0.55 0.15 255);
```

### Layer 2: Semantic Tokens

Context-aware tokens that define HOW styles are applied. Components use these:

```css
:root {
  --primary: oklch(0.21 0.034 264.665);
  --primary-foreground: oklch(0.985 0.002 247.839);
}
```

## Naming Convention

Follow the shadcn/taki-ui convention:

| Token                 | Purpose                       |
| --------------------- | ----------------------------- |
| `--{name}`            | Background/fill color         |
| `--{name}-foreground` | Text color ON that background |

```tsx
<button className="bg-primary text-primary-foreground">Click me</button>
```

## Conceptual Token Categories

Our semantic tokens are organized by **purpose**, not by visual property. This helps clarify when to use which token.

### Surface Tokens (Elevation Hierarchy)

Surface tokens define visual depth:

```css
:root {
  --surface-recessed: oklch(...); /* Inset areas: tracks, tab lists, footers */
  --surface-default: oklch(...); /* Main page background */
  --surface-subtle: oklch(...); /* Slightly elevated: cards, alerts */
  --surface-raised: oklch(...); /* Floating: popovers, tooltips */
}
```

| Token                | Use For               | Examples                                  |
| -------------------- | --------------------- | ----------------------------------------- |
| `--surface-recessed` | Inset/depressed areas | Progress tracks, tab lists, table footers |
| `--surface-default`  | Main background       | Page background                           |
| `--surface-subtle`   | Slightly elevated     | Cards, alerts                             |
| `--surface-raised`   | Floating elements     | Popovers, tooltips                        |

### Overlay Tokens

For modal backdrops and scrim layers:

```css
:root {
  --overlay: oklch(0 0 0 / 50%); /* Standard modal backdrop */
  --overlay-subtle: oklch(0 0 0 / 10%); /* Light backdrop with blur */
}
```

| Token              | Use For                    | Examples             |
| ------------------ | -------------------------- | -------------------- |
| `--overlay`        | Full modal backdrops       | Modal, Sheet, Dialog |
| `--overlay-subtle` | Subtle backdrops with blur | Drawer               |

### Status Tokens (Persistent State)

Status tokens represent **current state** that is always present until the state changes:

```css
:root {
  --success: oklch(...); /* Solid background */
  --success-foreground: oklch(...); /* Text ON solid */
}
```

**Use status tokens for:**

- Badges showing task state (completed, in-progress)
- Pipeline status indicators
- Priority levels
- System health indicators

```tsx
<Badge className="bg-success text-success-foreground">Complete</Badge>
```

### Feedback Tokens (Transient Notifications)

Feedback tokens are for **dynamic information** triggered by events that often requires action:

```css
:root {
  --success-subtle: oklch(...); /* Tinted background */
  --success-subtle-foreground: oklch(...); /* Dark text ON tint */
}
```

**Use feedback tokens (subtle variants) for:**

- Toast notifications
- Alert banners
- Validation messages
- Inline notices

```tsx
<Note
  intent="success"
  className="bg-success-subtle text-success-subtle-foreground"
>
  Changes saved successfully.
</Note>
```

### Status vs Feedback Decision Guide

| Characteristic | Status (solid)      | Feedback (subtle)   |
| -------------- | ------------------- | ------------------- |
| Purpose        | Current state       | Event notification  |
| Timing         | Always present      | Triggered by events |
| Persistence    | Until state changes | Often temporary     |
| Action needed? | Informational       | May require action  |
| Examples       | Badge, indicator    | Toast, Alert, Note  |

### Highlight Tokens (Emphasis)

Highlight tokens draw attention to content **without implying semantic meaning**:

```css
:root {
  --highlight-match: oklch(...); /* Search matches */
  --highlight-match-foreground: oklch(...);
  --highlight-target: oklch(...); /* URL targets */
  --highlight-target-foreground: oklch(...);
}
```

| Token                | Use For                       | Examples                       |
| -------------------- | ----------------------------- | ------------------------------ |
| `--highlight-match`  | Matched search/filter results | Command palette matches        |
| `--highlight-target` | URL anchor targets, scroll-to | `:target` pseudo-class styling |

```tsx
// Search match highlighting
<mark className="bg-highlight-match text-highlight-match-foreground">
  matched text
</mark>

// Scroll-to target
<section id="section" className="target:bg-highlight-target">
  Linked section
</section>
```

## Interactive State Tokens (When to Use)

Interactive states (`hover`, `focus`, `active`, `disabled`) can be handled two ways:

### Approach 1: Tailwind Variants (Default)

For most components, use Tailwind's built-in state variants with existing tokens:

```tsx
<Button className="bg-primary hover:bg-primary/90 focus:ring-ring">
  Click me
</Button>
```

**Advantages:**

- No extra tokens to maintain
- Follows Tailwind conventions
- State logic stays with components

### Approach 2: Explicit State Tokens (When Needed)

Create explicit state tokens when:

1. **Complex state calculations** - The hover color isn't a simple opacity/shade change
2. **Cross-component consistency** - Multiple components must share exact state colors
3. **Design system requirements** - Designers specify exact state values

```css
:root {
  /* Action tokens with explicit states */
  --action-primary: oklch(0.55 0.15 255);
  --action-primary-hover: oklch(0.5 0.16 255);
  --action-primary-active: oklch(0.45 0.17 255);
  --action-primary-disabled: oklch(0.55 0.05 255);

  /* Focus ring variations */
  --ring-default: oklch(0.55 0.15 255);
  --ring-error: oklch(0.55 0.2 25);
}
```

```tsx
<Button className="bg-action-primary hover:bg-action-primary-hover active:bg-action-primary-active">
  Click me
</Button>
```

### State Token Naming Convention

If you need state tokens, follow this pattern:

```text
--{category}-{concept}-{variant}-{state}
```

| State      | Description                             |
| ---------- | --------------------------------------- |
| `default`  | Normal resting state (often omitted)    |
| `hover`    | Pointer positioned over element         |
| `active`   | Element being pressed/clicked           |
| `focus`    | Element can accept input (keyboard nav) |
| `disabled` | Element cannot accept interaction       |
| `selected` | Element is currently selected           |
| `error`    | Element is in an error/invalid state    |

### Current Approach

Our UI package uses **Approach 1** (Tailwind variants) for most interactive states. This keeps the token count manageable and leverages Tailwind's built-in state handling.

Explicit state tokens are reserved for:

- Focus rings (`--ring`)
- Complex interactive patterns where opacity modifiers aren't sufficient

## Complete Status Color Pattern

Each status color needs 4 tokens to support both solid and subtle use cases:

```css
:root {
  /* Solid background (status/badges) */
  --info: oklch(...);
  --info-foreground: oklch(...);

  /* Subtle/tinted background (feedback/alerts) */
  --info-subtle: oklch(...);
  --info-subtle-foreground: oklch(...);
}
```

Status colors: `info`, `warning`, `success`, `destructive`

## Dark Mode

Semantic tokens change values between themes, but token NAMES stay the same:

```css
:root {
  --info-subtle: oklch(0.97 0.02 255); /* Light: light blue tint */
  --info-subtle-foreground: oklch(0.35 0.15 255); /* Dark blue text */
}

.dark {
  --info-subtle: oklch(0.22 0.04 255); /* Dark: dark blue tint */
  --info-subtle-foreground: oklch(0.75 0.12 255); /* Light blue text */
}
```

Components automatically adapt without code changes.

## Multi-Brand Theming (Advanced)

For applications that need multiple brand themes beyond light/dark, use `data-theme` attribute selectors.

### Adding Additional Themes

```css
/* theme.css - Add after .dark block */

/* Brand themes using data-theme attribute */
[data-theme='brand-blue'] {
  --primary: oklch(0.55 0.18 255);
  --primary-foreground: oklch(0.98 0 0);
  --accent: oklch(0.45 0.15 255);
  --accent-foreground: oklch(0.98 0 0);
}

[data-theme='brand-green'] {
  --primary: oklch(0.55 0.18 145);
  --primary-foreground: oklch(0.98 0 0);
  --accent: oklch(0.45 0.15 145);
  --accent-foreground: oklch(0.98 0 0);
}
```

### Applying Themes

```tsx
// Set theme on root element
<html data-theme="brand-blue">
  <body>
    <Button>Uses brand-blue colors</Button>
  </body>
</html>;

// Or switch dynamically
function setTheme(theme: string) {
  document.documentElement.setAttribute('data-theme', theme);
}
```

### Combining with Dark Mode

For brands that also need dark mode support:

```css
[data-theme='brand-blue'] {
  --primary: oklch(0.55 0.18 255);
}

[data-theme='brand-blue'].dark {
  --primary: oklch(0.65 0.15 255);
}
```

```tsx
// Both brand AND mode
<html data-theme="brand-blue" class="dark">
```

### When to Use Multi-Brand Theming

- White-label products serving multiple customers
- Sub-brands within a product family
- Seasonal or promotional themes
- A/B testing different color schemes

### When NOT to Use

- Simple light/dark mode (use `.dark` class)
- One-off color overrides (use inline styles or component props)
- Per-component styling (use component variants)

## Scoped Theming (Widgets & Embedded Components)

For components that need their own theme independent of the page:

```tsx
// Widget with its own theme, ignoring parent
<div
  data-theme="widget-dark"
  className="rounded-lg p-4 bg-background text-foreground"
>
  <h2>This widget always uses dark theme</h2>
  <Button>Styled with widget-dark tokens</Button>
</div>
```

```css
/* Scoped theme for embedded widget */
[data-theme='widget-dark'] {
  --background: oklch(0.15 0.02 260);
  --foreground: oklch(0.95 0 0);
  --primary: oklch(0.6 0.15 255);
  --primary-foreground: oklch(0.98 0 0);
}
```

**Use cases:**

- Embeddable widgets (Figma plugins, iframe content)
- Preview panels that show different themes
- Marketing sections with distinct styling

## Enhanced Primitives Pattern (Scaling Strategy)

For large teams or multi-product organizations, consider wrapping base components with organization-wide enhancements.

### The Pattern

```tsx
// packages/enhanced-primitives/src/smart-button.tsx
import { Button, type ButtonProps } from '@oakoss/ui/button';

interface SmartButtonProps extends ButtonProps {
  /** Analytics event ID */
  trackingId?: string;
  /** Additional tracking data */
  trackingData?: Record<string, unknown>;
  /** Error callback */
  onError?: (error: Error) => void;
  /** Debounce rapid clicks (ms) */
  debounceMs?: number;
}

export function SmartButton({
  trackingId,
  trackingData,
  onError,
  debounceMs = 0,
  onClick,
  children,
  ...props
}: SmartButtonProps) {
  const { track } = useAnalytics();
  const [isDebouncing, setIsDebouncing] = useState(false);

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    // Debounce
    if (debounceMs > 0 && isDebouncing) return;
    if (debounceMs > 0) {
      setIsDebouncing(true);
      setTimeout(() => setIsDebouncing(false), debounceMs);
    }

    // Analytics
    if (trackingId) {
      track(trackingId, { component: 'SmartButton', ...trackingData });
    }

    // Error boundary
    try {
      onClick?.(e);
    } catch (error) {
      onError?.(error as Error);
    }
  };

  return (
    <Button onClick={handleClick} {...props}>
      {children}
    </Button>
  );
}
```

### Layer Architecture

```text
Layer 4: Application Components    ← Team-specific (UserDashboard, CheckoutForm)
Layer 3: Composed Patterns         ← Domain patterns (ProductCard, MetricCard)
Layer 2: Enhanced Primitives       ← Org-wide (SmartButton, TrackedLink)
Layer 1: Foundation (@oakoss/ui)   ← Base components + design tokens
```

### When to Use Enhanced Primitives

- **Multiple products** need consistent analytics/error handling
- **Cross-cutting concerns** that apply to many components
- **Organization-wide requirements** (accessibility announcements, loading states)

### When NOT to Use

- **Single product** - adds unnecessary abstraction
- **Small team** - coordination overhead outweighs benefits
- **Simple use cases** - just use base components directly

### Implementation Notes

- Keep enhanced primitives in a separate package (`@company/enhanced-ui`)
- Don't modify the base UI package - extend it
- Enhanced primitives should be drop-in replacements (same base API)
- Document which enhancements each wrapper provides

## Typography Tokens

### Font Family

We use Inter Variable as the primary sans-serif font, loaded via `@fontsource-variable/inter`:

```css
@theme inline {
  --font-sans: 'Inter Variable', sans-serif;
}
```

### Font Loading Strategy

**Why Fontsource?**

- **Automatic `@font-face` declarations** - No manual font file hosting
- **Variable font support** - Single file for all weights (100-900)
- **Unicode subsetting** - Separate files per language for smaller bundles
- **`font-display: swap`** - Better loading performance (text visible immediately)

**How it works:**

```css
/* In globals.css (app entry point) */
@import '@fontsource-variable/inter';
@import '@oakoss/ui/theme.css';

@theme inline {
  --font-sans: 'Inter Variable', sans-serif;
}
```

The fontsource package provides:

```css
/* Auto-generated @font-face declarations */
@font-face {
  font-family: 'Inter Variable';
  font-style: normal;
  font-display: swap;
  font-weight: 100 900;
  src: url(./files/inter-latin-wght-normal.woff2) format('woff2-variations');
  unicode-range: U+0000-00FF, ...;
}
```

### Font Configuration in Theme

The font token is registered in the `@theme inline` block:

```css
@theme inline {
  /* Typography */
  --font-sans: 'Inter Variable', sans-serif;

  /* Colors... */
}
```

This makes `font-sans` available as a Tailwind utility class.

### Using Fonts in Components

```tsx
// Via Tailwind (preferred)
<body className="font-sans">

// Base layer applies font globally
@layer base {
  body {
    @apply font-sans bg-background text-foreground;
  }
}
```

### Adding Additional Fonts

To add a new font family:

1. **Install the fontsource package:**

   ```bash
   pnpm --filter @oakoss/ui add @fontsource-variable/geist-mono
   ```

2. **Import in globals.css:**

   ```css
   @import '@fontsource-variable/geist-mono';
   ```

3. **Register in @theme inline:**

   ```css
   @theme inline {
     --font-sans: 'Inter Variable', sans-serif;
     --font-mono: 'Geist Mono Variable', ui-monospace, monospace;
   }
   ```

4. **Use in components:**

   ```tsx
   <code className="font-mono">const x = 42;</code>
   ```

### Font Weight Considerations

Inter Variable supports weights 100-900. Common usage:

| Weight | Name       | Use For                             |
| ------ | ---------- | ----------------------------------- |
| 400    | `normal`   | Body text, descriptions             |
| 500    | `medium`   | Labels, navigation, subtle emphasis |
| 600    | `semibold` | Headings, buttons, strong emphasis  |
| 700    | `bold`     | Hero headings, critical actions     |

```tsx
<p className="font-normal">Body text</p>
<label className="font-medium">Form label</label>
<h1 className="font-semibold">Page title</h1>
<span className="font-bold">Important</span>
```

## OKLCH Color Format

Use OKLCH for perceptually uniform colors:

```css
--color: oklch(L C H);
/* L = Lightness (0-1): 0 = black, 1 = white */
/* C = Chroma (0-0.4): color saturation */
/* H = Hue (0-360): color wheel angle */
```

Common hue values:

| Color           | Hue     |
| --------------- | ------- |
| Red/Destructive | 22-30   |
| Orange/Warning  | 70-85   |
| Yellow          | 95-110  |
| Green/Success   | 145-170 |
| Cyan            | 195-210 |
| Blue/Info       | 250-265 |
| Purple          | 285-310 |

## Accessibility Requirements

All color pairings MUST meet WCAG AA contrast ratios:

| Context                         | Minimum Ratio |
| ------------------------------- | ------------- |
| Normal text                     | 4.5:1         |
| Large text (18px+ or 14px bold) | 3:1           |
| UI components                   | 3:1           |

### Testing Contrast

Always test both light AND dark modes:

```bash
pnpm test:storybook:both
```

### Common Contrast Issues

1. **Muted text on muted background** - Ensure `--muted-foreground` has 4.5:1 on `--muted`
2. **Status colors on tinted backgrounds** - The `*-subtle-foreground` must contrast with `*-subtle`
3. **Highlight backgrounds** - Ensure foreground text meets contrast on highlight colors

## Registering Tokens in @theme

All semantic tokens must be registered in the `@theme inline` block:

```css
@theme inline {
  --color-info: var(--info);
  --color-info-foreground: var(--info-foreground);
  --color-info-subtle: var(--info-subtle);
  --color-info-subtle-foreground: var(--info-subtle-foreground);
  --color-highlight-match: var(--highlight-match);
  --color-highlight-match-foreground: var(--highlight-match-foreground);
}
```

This makes them available as Tailwind utilities (`bg-info`, `text-highlight-match-foreground`, etc.).

## Avoid Hardcoded Colors

Never use raw Tailwind colors in components:

```tsx
// BAD - hardcoded colors
<Badge className="bg-blue-500 text-white dark:bg-blue-400">

// GOOD - semantic tokens
<Badge className="bg-info text-info-foreground">
```

Hardcoded colors:

- Break theme consistency
- Require manual dark mode handling
- Make rebranding difficult
- Often fail accessibility tests

## Custom Responsive Utilities with @layer components

For page layouts that need responsive spacing, typography, or other utilities that scale across breakpoints, use the `@layer components` directive in your application's CSS.

**Why not in the UI package?**

- UI components should be layout-agnostic and work at any size
- Responsive behavior belongs at the layout/page level
- Applications have different breakpoint needs

### Creating Responsive Spacing Utilities

Add to your app's global CSS (not the UI package):

```css
@layer components {
  /* Responsive gap utilities */
  .gap-responsive-sm {
    @apply gap-2 md:gap-3 lg:gap-4;
  }
  .gap-responsive-md {
    @apply gap-4 md:gap-5 lg:gap-6;
  }
  .gap-responsive-lg {
    @apply gap-6 md:gap-8 lg:gap-10;
  }

  /* Responsive padding utilities */
  .p-responsive-sm {
    @apply p-3 md:p-4 lg:p-5;
  }
  .p-responsive-md {
    @apply p-4 md:p-6 lg:p-8;
  }
  .p-responsive-lg {
    @apply p-6 md:p-8 lg:p-12;
  }

  /* Section/container spacing */
  .section-padding {
    @apply px-4 py-12 md:px-6 md:py-16 lg:px-8 lg:py-20;
  }
  .container-padding {
    @apply px-4 md:px-6 lg:px-8;
  }
}
```

### Creating Responsive Typography Utilities

```css
@layer components {
  /* Responsive headings */
  .text-display {
    @apply text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight;
  }
  .text-title {
    @apply text-xl md:text-2xl lg:text-3xl font-semibold;
  }
  .text-subtitle {
    @apply text-lg md:text-xl font-medium;
  }

  /* Responsive body text */
  .text-body-lg {
    @apply text-base md:text-lg leading-relaxed;
  }
}
```

### Usage in Components

```tsx
// Page layout with responsive spacing
<main className="section-padding">
  <div className="container-padding max-w-7xl mx-auto">
    <h1 className="text-display mb-6">Welcome</h1>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-responsive-md">
      {/* Cards automatically get responsive gaps */}
    </div>
  </div>
</main>
```

### Why Use @layer components?

1. **Proper specificity** - Won't override utility classes when you need one-offs
2. **Organized** - Keeps custom utilities separate from Tailwind's built-ins
3. **Purge-safe** - Tailwind's purge respects @layer directives
4. **Composable** - Can still add breakpoint-specific overrides: `gap-responsive-md lg:gap-8`

### Naming Convention

Use descriptive names that won't conflict with Tailwind's utilities:

- `gap-responsive-*` instead of `gap-sm` (could conflict)
- `p-responsive-*` instead of `p-sm`
- `section-*` for page-level patterns
- `text-display`, `text-title` for typography roles

## Adding New Tokens Checklist

When adding a new semantic token:

1. Define in `:root` (light mode value)
2. Define in `.dark` (dark mode value)
3. Register in `@theme inline` block
4. Test contrast in both modes
5. Update component to use the token
6. Run `pnpm test:storybook:both`
