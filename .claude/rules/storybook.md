---
paths:
  - 'skills/storybook-stories/references/**'
  - 'skills/**/references/*stories*'
  - 'skills/**/references/*storybook*'
  - 'skills/**/references/*interaction-test*'
---

# Storybook Rules

Conventions for code examples in Storybook and component story skill references.

## Story Structure

```tsx
import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, fn, userEvent, within } from 'storybook/test';

const meta = {
  component: Button,
  tags: ['autodocs'],
  title: 'Components/Button',
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Click me',
  },
};
```

## Story Naming

| Type         | Convention            | Example                                   |
| ------------ | --------------------- | ----------------------------------------- |
| Default      | `Default`             | `export const Default: Story`             |
| Variants     | Variant name          | `Secondary`, `Destructive`, `Ghost`       |
| Sizes        | Size name             | `Small`, `Large`                          |
| States       | State description     | `Disabled`, `Loading`                     |
| Interactions | `{Action}Interaction` | `ClickInteraction`, `KeyboardInteraction` |

## Story Consolidation

Prefer fewer, denser stories over many single-purpose stories. Every story file renders a11y checks and Chromatic snapshots automatically — visual coverage comes from rendering the component, not from having a dedicated story per state.

### Consolidation Rules

1. **Group related visual states into one story.** If multiple stories only differ by a single prop (checked, indeterminate, invalid, read-only), combine them into a `States` story that renders all variants together.

2. **Merge interaction tests into visual stories when they share the same render.** If a `Disabled` story and a `DisabledInteraction` story render the same thing, add the `play` function directly to the visual story.

3. **Don't create stories that duplicate what controls already provide.** The `Default` story with args/controls already lets users toggle every prop. A separate `Checked` story that only sets `defaultSelected: true` adds a snapshot but no new information.

4. **Remove interaction tests made redundant by component design.** If the component wraps children in a `<label>`, a "click the label" test is identical to a "click the checkbox" test.

### Story Categories

Each component should have these categories (only when applicable):

| Category                | Purpose                                                | Has `play`?                   |
| ----------------------- | ------------------------------------------------------ | ----------------------------- |
| **Default**             | Interactive playground with all controls               | No                            |
| **States**              | All visual states in one view (checked, invalid, etc.) | No                            |
| **Variants**            | Variant showcase (sizes, colors)                       | No                            |
| **Disabled**            | All disabled combinations                              | Yes — assert `toBeDisabled()` |
| **{Pattern}Controlled** | Complex stateful patterns (indeterminate parent/child) | No                            |
| **ClickInteraction**    | Mouse toggle + onChange assertion                      | Yes                           |
| **KeyboardInteraction** | Tab focus + keyboard toggle                            | Yes                           |

### Example: Consolidated Checkbox (7 stories vs 12)

```tsx
// States - replaces Checked, Indeterminate, Invalid, ReadOnly
export const States: Story = {
  render: () => (
    <div className="flex flex-col gap-3">
      <Checkbox defaultSelected>Checked</Checkbox>
      <Checkbox isIndeterminate>Indeterminate</Checkbox>
      <Checkbox isInvalid>Invalid</Checkbox>
      <Checkbox defaultSelected isReadOnly>
        Read only
      </Checkbox>
    </div>
  ),
};

// Disabled - visual + interaction merged
export const Disabled: Story = {
  args: { onChange: fn() },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const checkboxes = canvas.getAllByRole('checkbox');
    await expect(checkboxes[0]).toBeDisabled();
    await expect(args.onChange).not.toHaveBeenCalled();
  },
  render: () => (
    <div className="flex flex-col gap-3">
      <Checkbox isDisabled>Disabled unchecked</Checkbox>
      <Checkbox defaultSelected isDisabled>
        Disabled checked
      </Checkbox>
      <Checkbox isDisabled isIndeterminate>
        Disabled indeterminate
      </Checkbox>
    </div>
  ),
};
```

### When NOT to Consolidate

- **Complex stateful patterns** (IndeterminateControlled) — keep separate, they demonstrate real usage
- **Different render structures** — stories with different DOM shapes serve different visual regression purposes
- **Different interaction modalities** — keep ClickInteraction and KeyboardInteraction separate since they test different input methods

## Light/Dark Mode Testing

Test both light and dark modes for visual regression and a11y coverage. Use environment variables or test scripts to control which mode runs.

## Portal-Rendered Components

Dialogs, modals, popovers, and tooltips render in **portals** outside the Storybook canvas. You must search `document.body` to find them:

```tsx
play: async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  const body = within(canvasElement.ownerDocument.body); // Search portals

  // Trigger is in canvas
  await userEvent.click(canvas.getByRole('button', { name: 'Open' }));

  // Dialog renders in portal - search body, not canvas
  const dialog = await body.findByRole('dialog');
  await expect(dialog).toBeInTheDocument();
},
```

| Component Type  | Renders In | Search With                   |
| --------------- | ---------- | ----------------------------- |
| Buttons, forms  | Canvas     | `canvas.getByRole()`          |
| Dialog, Modal   | Portal     | `body.findByRole('dialog')`   |
| Sheet, Drawer   | Portal     | `body.findByRole('dialog')`   |
| Popover         | Portal     | `body.findByRole('dialog')`   |
| HoverCard       | Portal     | `body.findByRole('dialog')`   |
| Tooltip         | Portal     | `body.findByRole('tooltip')`  |
| Select          | Portal     | `body.findByRole('listbox')`  |
| ComboBox        | Portal     | `body.findByRole('listbox')`  |
| MultipleSelect  | Portal     | `body.findByRole('listbox')`  |
| DropdownMenu    | Portal     | `body.findByRole('menu')`     |
| ContextMenu     | Portal     | `body.findByRole('menu')`     |
| Menubar content | Portal     | `body.findByRole('menu')`     |
| DatePicker      | Portal     | `body.findByRole('dialog')`   |
| DateRangePicker | Portal     | `body.findByRole('dialog')`   |
| ListBox         | Canvas     | `canvas.getByRole('listbox')` |

## Component Trigger Roles

Different form components use different ARIA roles for their triggers:

| Component      | Trigger Role | How to Open                          |
| -------------- | ------------ | ------------------------------------ |
| Select         | `button`     | Click trigger                        |
| ComboBox       | `combobox`   | Click + ArrowDown (more reliable)    |
| MultipleSelect | `button`     | Click trigger (note: NOT `combobox`) |

```tsx
// Select - uses button role
const trigger = canvas.getByRole('button', { name: /Country/i });
await userEvent.click(trigger);

// ComboBox - uses combobox role, ArrowDown to open reliably
const input = canvas.getByRole('combobox');
await userEvent.click(input);
await userEvent.keyboard('{ArrowDown}');

// MultipleSelect - uses button role (NOT combobox)
const trigger = canvas.getByRole('button', { name: /Tags/i });
await userEvent.click(trigger);
```

## ARIA Roles by Component

| Component   | Selection Mode | Query Role | Attribute      |
| ----------- | -------------- | ---------- | -------------- |
| ToggleGroup | `single`       | `radio`    | `aria-checked` |
| ToggleGroup | `multiple`     | `button`   | `aria-pressed` |
| RadioGroup  | -              | `radio`    | `aria-checked` |
| Checkbox    | -              | `checkbox` | `aria-checked` |
| Switch      | -              | `switch`   | `aria-checked` |
| Toggle      | -              | `button`   | `aria-pressed` |

```tsx
// Single selection ToggleGroup (radio group)
const radios = canvas.getAllByRole('radio');
await expect(radios[0]).toHaveAttribute('aria-checked', 'true');

// Multiple selection ToggleGroup (toolbar with toggle buttons)
const buttons = canvas.getAllByRole('button');
await expect(buttons[0]).toHaveAttribute('aria-pressed', 'true');
```

## Trigger Pattern (Avoiding Nested Buttons)

RAC container components use the `slot` prop to identify triggers. Pass `Button` directly with the slot instead of wrapping:

```tsx
// GOOD - Button with slot="trigger"
<Sheet>
  <Button variant="outline">Open Sheet</Button>
  <SheetContent>
    <Button slot="close" variant="outline">Done</Button>
  </SheetContent>
</Sheet>

// BAD - Nested buttons create invalid HTML
<Sheet>
  <SheetTrigger>
    <Button variant="outline">Open Sheet</Button>  {/* Button inside button! */}
  </SheetTrigger>
</Sheet>
```

**Components that ARE buttons (don't wrap):** `SheetTrigger`, `DrawerTrigger`, `PopoverTrigger`, `CollapsibleTrigger`

**Components that are containers (pass Button as child):** `DialogTrigger`, `Sheet`, `Drawer`, `Popover`, `Collapsible`

## Interaction Test Pattern

```tsx
export const OpenCloseInteraction: Story = {
  args: {
    onOpenChange: fn(), // Track state changes
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);

    // Open
    const trigger = canvas.getByRole('button', { name: 'Open' });
    await userEvent.click(trigger);
    await expect(args.onOpenChange).toHaveBeenCalledWith(true);

    // Verify dialog exists
    const dialog = await body.findByRole('dialog');
    await expect(dialog).toBeInTheDocument();

    // Close via button
    const closeButton = within(dialog).getByRole('button', { name: 'Done' });
    await userEvent.click(closeButton);
    await expect(args.onOpenChange).toHaveBeenCalledWith(false);
  },
};
```

## Keyboard Navigation Test

```tsx
export const KeyboardInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);

    // Tab to trigger and open with Enter
    await userEvent.tab();
    await userEvent.keyboard('{Enter}');

    const dialog = await body.findByRole('dialog');
    await expect(dialog).toBeInTheDocument();

    // Close with Escape
    await userEvent.keyboard('{Escape}');
  },
};
```

## Animated Components

Components using motion/framer-motion animate before callbacks fire. Use `waitFor`:

```tsx
import { expect, fn, userEvent, waitFor, within } from 'storybook/test';

export const AnimatedClose: Story = {
  args: {
    onOpenChange: fn(),
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);

    await userEvent.click(canvas.getByRole('button', { name: 'Open' }));
    const dialog = await body.findByRole('dialog');
    await userEvent.click(
      within(dialog).getByRole('button', { name: 'Close' }),
    );

    // Animation completes before callback fires - use waitFor
    await waitFor(async () => {
      await expect(args.onOpenChange).toHaveBeenCalledWith(false);
    });
  },
};
```

Components that animate: Drawer, some modals with custom transitions.

## Browser Connection Stability

Vitest browser mode config for stability:

```ts
// vitest.config.ts
test: {
  fileParallelism: false,    // Run tests sequentially
  hookTimeout: 30000,        // 30s for setup/teardown
  testTimeout: 30000,        // 30s per test
  teardownTimeout: 10000,    // Allow browser to close gracefully
  isolate: true,             // Isolate test files
  retry: process.env.CI ? 2 : 0,  // Retry in CI
}
```

## Link Interaction Tests

**Critical:** Use `href=""` (empty string) instead of `href="#"` for interaction tests. Hash hrefs trigger navigation which crashes Vitest browser mode.

```tsx
// BAD - causes browser crashes
export const ClickInteraction: Story = {
  play: async ({ canvasElement }) => {
    const link = within(canvasElement).getByRole('link');
    await userEvent.click(link); // Navigates to "#", crashes browser
  },
  render: () => <Link href="#">Click me</Link>,
};

// GOOD - empty href prevents navigation
export const ClickInteraction: Story = {
  play: async ({ canvasElement }) => {
    const link = within(canvasElement).getByRole('link');
    await userEvent.click(link); // No navigation, test passes
  },
  render: () => <Link href="">Click me</Link>,
};
```

React Aria Link requires an `href` prop, but empty string satisfies this while preventing navigation.

## Roving Tabindex Focus Pattern

React Aria components like GridList, TagGroup, and Tree use **roving tabindex** for keyboard navigation. When tabbing into the component, focus goes to the **first item**, not the container.

```tsx
// BAD - expects focus on container
export const KeyboardNavigation: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.tab();
    // This will FAIL - container doesn't receive focus
    await expect(canvas.getByRole('grid')).toHaveFocus();
  },
};

// GOOD - expects focus on first item
export const KeyboardNavigation: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.tab();
    // Focus goes to first row, not the grid container
    const rows = canvas.getAllByRole('row');
    await expect(rows[0]).toHaveFocus();
  },
};
```

**Components using roving tabindex:** GridList, TagGroup, Tree, Menu, ListBox

## React Aria Collection Components

React Aria collection components (ListBox, GridList, Tree, Breadcrumb) render children asynchronously. The play function can trigger before the collection hydrates, causing `getAllByRole` to return empty arrays.

**Always use async queries** (`findAllByRole`) for collection components:

```tsx
// BAD - sync query returns empty array before hydration
export const SelectionInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const options = canvas.getAllByRole('option'); // Returns [] in Chromatic!
    await userEvent.click(options[0]!); // Fails
  },
};

// GOOD - async query waits for elements to appear
export const SelectionInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const listbox = canvas.getByRole('listbox');
    // Use findAllByRole to wait for React Aria collection to hydrate
    const options = await within(listbox).findAllByRole('option');
    await userEvent.click(options[0]!);
  },
};
```

| Component  | Container Role | Item Role  | Async Query                 |
| ---------- | -------------- | ---------- | --------------------------- |
| ListBox    | `listbox`      | `option`   | `findAllByRole('option')`   |
| GridList   | `grid`         | `row`      | `findAllByRole('row')`      |
| Tree       | `treegrid`     | `row`      | `findAllByRole('row')`      |
| Breadcrumb | `list`         | `link`     | `findAllByRole('link')`     |
| Menu       | `menu`         | `menuitem` | `findAllByRole('menuitem')` |

## Async Component Initialization

Some components (Embla Carousel, etc.) initialize asynchronously. Buttons may be disabled until the API is ready. Use `waitFor` to wait for the component to be interactive:

```tsx
import { expect, userEvent, waitFor, within } from 'storybook/test';

export const NavigationInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const nextButton = canvas.getByRole('button', { name: /next/i });

    // Wait for Embla carousel API to initialize and enable the button
    await waitFor(async () => {
      await expect(nextButton).not.toBeDisabled();
    });

    await userEvent.click(nextButton);
  },
};
```

## Tooltip and Hover Testing

**Critical:** `userEvent.hover()` is unreliable in headless browsers (Chromatic, CI). React Aria's `useTooltipTrigger` checks `interactionModality` and won't open tooltips unless it detects a real pointer event.

**Use keyboard focus instead of hover** for tooltip interaction tests:

```tsx
// BAD - hover is unreliable in headless browsers
export const HoverInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    const trigger = canvas.getByRole('button');

    await userEvent.hover(trigger); // Unreliable in Chromatic!
    const tooltip = await body.findByRole('tooltip'); // May never appear
  },
};

// GOOD - keyboard focus reliably triggers tooltips
export const HoverInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    const trigger = canvas.getByRole('button');

    // userEvent.tab() properly triggers React Aria's focus-based tooltip
    await userEvent.tab();
    await expect(trigger).toHaveFocus();

    const tooltip = await body.findByRole('tooltip');
    await expect(tooltip).toBeInTheDocument();
  },
};
```

React Aria tooltips appear on both hover AND focus, so using focus for tests is valid and more reliable.

## Date/Time Field Keyboard Tests

DateField and TimeField require a `defaultValue` for keyboard interaction tests. Without a value, keyboard navigation has no segments to move between.

```tsx
// BAD - no value, keyboard test fails
export const KeyboardInteraction: Story = {
  play: async ({ canvasElement }) => {
    await userEvent.tab();
    await userEvent.keyboard('{ArrowRight}'); // No segments to navigate
  },
  render: () => <DateField label="Date" />,
};

// GOOD - defaultValue provides segments
export const KeyboardInteraction: Story = {
  play: async ({ canvasElement }) => {
    await userEvent.tab();
    await userEvent.keyboard('{ArrowRight}'); // Navigates between segments
  },
  render: () => (
    <DateField defaultValue={parseDate('2024-01-15')} label="Date" />
  ),
};
```

## Axe A11y Rule Overrides

Some axe rules need to be disabled for valid React Aria patterns. Use sparingly and document why.

### link-in-text-block

Standalone links (not inside paragraph text) trigger this rule. Disable when the link is intentionally standalone:

```tsx
export const Default: Story = {
  parameters: {
    a11y: {
      config: {
        // Standalone link - not inside a text block, so rule doesn't apply
        rules: [{ id: 'link-in-text-block', enabled: false }],
      },
    },
  },
  render: () => <Link href="">Standalone Link</Link>,
};
```

### aria-required-children

React Aria menus use non-standard but accessible patterns. Menu headers (`role="presentation"`) inside menus trigger this:

```tsx
export const WithHeader: Story = {
  parameters: {
    a11y: {
      config: {
        // React Aria menu headers use role="presentation" which axe flags
        rules: [{ id: 'aria-required-children', enabled: false }],
      },
    },
  },
};
```

### aria-allowed-attr

Some upstream libraries have ARIA issues. Document and track separately:

```tsx
export const Resizable: Story = {
  parameters: {
    a11y: {
      config: {
        // Upstream react-resizable-panels issue - aria-orientation on separator
        // Tracked: https://github.com/bvaughn/react-resizable-panels/issues/XXX
        rules: [{ id: 'aria-allowed-attr', enabled: false }],
      },
    },
  },
};
```

### When to Override vs Fix

| Situation                      | Action                            |
| ------------------------------ | --------------------------------- |
| Upstream library issue         | Override with tracking comment    |
| React Aria intentional pattern | Override with explanation         |
| Your component has the issue   | Fix the component, don't override |
| Unsure                         | Investigate before overriding     |

## Component-Specific Rule Exclusions

Reference of all permanent rule exclusions in the UI library:

### Command (stories with separators)

| Rule                     | Reason                                                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| `aria-required-children` | cmdk renders `role="separator"` inside `role="listbox"`. ARIA requires listbox children to be option or group only. |

### Command (Empty story)

| Rule                     | Reason                                                                                                         |
| ------------------------ | -------------------------------------------------------------------------------------------------------------- |
| `aria-required-children` | cmdk renders empty listbox when no items match filter. ARIA requires listbox to have option or group children. |

### DropdownMenu / Menubar (stories with headers)

| Rule                     | Reason                                                                                               |
| ------------------------ | ---------------------------------------------------------------------------------------------------- |
| `aria-required-children` | React Aria menu headers use `role="presentation"` inside menus, which axe flags as invalid children. |

### Resizable (all stories)

| Rule                | Reason                                                                                                                                        |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `aria-allowed-attr` | react-resizable-panels sets `aria-orientation` on Group div without a role. Only valid on separator, scrollbar, listbox, etc. Upstream issue. |

### Link (standalone stories)

| Rule                 | Reason                                                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `link-in-text-block` | axe expects links in text to be distinguishable. Standalone links outside paragraphs don't need this distinction. |
