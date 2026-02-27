---
title: Visual Testing
description: Chromatic visual regression testing, snapshot configuration, modes, viewports, and ignoring dynamic content
tags: [Chromatic, visual regression, snapshots, modes, viewports, ignore]
---

# Visual Testing

## Chromatic Overview

Chromatic captures pixel-perfect snapshots of stories and detects visual regressions. Configure snapshots using the `chromatic` parameter.

### Basic Setup

Configure global settings in `.storybook/preview.ts`:

```tsx
import { type Preview } from '@storybook/react';

const preview: Preview = {
  parameters: {
    chromatic: {
      delay: 300,
      diffThreshold: 0.1,
      modes: {
        dark: {
          theme: 'dark',
        },
        light: {
          theme: 'light',
        },
      },
    },
  },
};

export default preview;
```

### Per-Story Configuration

Override settings for individual stories:

```tsx
export const AnimatedComponent: Story = {
  parameters: {
    chromatic: {
      delay: 500,
      pauseAnimationAtEnd: true,
    },
  },
};
```

## Snapshot Modes

Capture stories in multiple themes or configurations:

```tsx
const preview: Preview = {
  parameters: {
    chromatic: {
      modes: {
        dark: { theme: 'dark' },
        light: { theme: 'light' },
      },
    },
  },
};
```

Override per story:

```tsx
export const LightOnly: Story = {
  parameters: {
    chromatic: { modes: { light: { theme: 'light' } } },
  },
};
```

## Viewports

Capture stories at different screen sizes:

```tsx
export const ResponsiveComponent: Story = {
  parameters: {
    chromatic: {
      viewports: [320, 768, 1200],
    },
  },
};
```

## Animation Handling

Wait for animations or pause them:

```tsx
export const WithAnimation: Story = {
  parameters: {
    chromatic: {
      delay: 1000,
      pauseAnimationAtEnd: true,
    },
  },
};
```

## Ignoring Dynamic Content

### Ignore Selectors

Ignore elements that change on every render:

```tsx
export const WithDynamicContent: Story = {
  parameters: {
    chromatic: {
      ignoreSelectors: ['.timestamp', '.random-avatar', '.live-data'],
    },
  },
};
```

### Ignore via ClassName

Add class to elements to ignore:

```tsx
export const WithClock: Story = {
  render: () => (
    <div>
      <h1>Dashboard</h1>
      <div className="chromatic-ignore">
        <Clock />
      </div>
    </div>
  ),
};
```

### Ignore via Data Attribute

```tsx
export const WithVideo: Story = {
  render: () => <video data-chromatic="ignore" src="video.mp4" />,
};
```

## Snapshot Control

### Disable Snapshot

Skip story in visual tests:

```tsx
export const InteractiveOnly: Story = {
  parameters: {
    chromatic: {
      disableSnapshot: true,
    },
  },
};
```

Use for stories with interaction tests but no visual regression value.

### Force Re-Snapshot

Force new baseline snapshot:

```tsx
export const Updated: Story = {
  parameters: {
    chromatic: {
      forcedReRender: true,
    },
  },
};
```

## Diff Threshold

### Global Threshold

Set sensitivity for all stories:

```tsx
const preview: Preview = {
  parameters: {
    chromatic: {
      diffThreshold: 0.2,
    },
  },
};
```

- `0.0` = Pixel-perfect (very sensitive)
- `0.5` = Moderate differences allowed
- `1.0` = Very lenient

### Per-Story Threshold

```tsx
export const SubtleGradient: Story = {
  parameters: {
    chromatic: {
      diffThreshold: 0.3,
    },
  },
};
```

## Story Isolation

Keep stories independent using args instead of play functions for initial state:

```tsx
export const OpenState: Story = {
  args: { defaultOpen: true },
};

export const ClosedState: Story = {
  args: { defaultOpen: false },
};
```

## CI Configuration

Run Chromatic in GitHub Actions:

```yaml
- uses: actions/checkout@v6
  with:
    fetch-depth: 0
- run: pnpm install
- run: pnpm chromatic --project-token=${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

Flags: `--exit-zero-on-changes` (prevent CI failure), `--auto-accept-changes main` (auto-accept on main), `--only-changed` (TurboSnap optimization).

## Interaction Tests with Snapshots

Capture snapshots after play function completes:

```tsx
export const AfterInteraction: Story = {
  parameters: {
    chromatic: {
      delay: 500,
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    const button = canvas.getByRole('button');
    await userEvent.click(button);

    // Wait for transition
    await new Promise((resolve) => setTimeout(resolve, 300));
  },
};
```

Chromatic captures the final state after play function execution.

## Debugging

Preview snapshots locally:

```bash
pnpm build-storybook
npx http-server storybook-static
```

Check diagnostics:

```bash
pnpm chromatic --diagnostics
```

## Common Patterns

### Modal Snapshots

```tsx
export const OpenModal: Story = {
  args: {
    defaultOpen: true,
  },
  parameters: {
    chromatic: {
      delay: 300,
    },
  },
};
```

### Tooltip Snapshots

```tsx
export const TooltipVisible: Story = {
  parameters: {
    chromatic: {
      delay: 500,
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('button');

    await userEvent.hover(trigger);
    await new Promise((resolve) => setTimeout(resolve, 200));
  },
};
```

### Form States

```tsx
export const FilledForm: Story = {
  parameters: {
    chromatic: {
      disableSnapshot: false,
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByLabelText('Email'), 'user@example.com');
    await userEvent.type(canvas.getByLabelText('Password'), 'password123');

    // Wait for validation
    await new Promise((resolve) => setTimeout(resolve, 100));
  },
};
```

### Error States

```tsx
export const ValidationError: Story = {
  args: {
    error: 'Email is required',
    touched: true,
  },
  parameters: {
    chromatic: {
      delay: 100,
    },
  },
};
```

Prefer args over play functions for static error states.
