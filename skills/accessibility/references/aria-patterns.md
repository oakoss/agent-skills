---
title: ARIA Patterns
description: Accessible tabs with arrow key navigation, ARIA live regions for dynamic content, and data tables with proper scope attributes
tags: [aria, tabs, live-regions, data-tables, keyboard-navigation]
---

# ARIA Patterns

## Accessible Tabs

```tsx
function Tabs({
  tabs,
}: {
  tabs: Array<{ label: string; content: React.ReactNode }>;
}) {
  const [activeIndex, setActiveIndex] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      setActiveIndex(index === 0 ? tabs.length - 1 : index - 1);
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      setActiveIndex(index === tabs.length - 1 ? 0 : index + 1);
    } else if (e.key === 'Home') {
      e.preventDefault();
      setActiveIndex(0);
    } else if (e.key === 'End') {
      e.preventDefault();
      setActiveIndex(tabs.length - 1);
    }
  };

  return (
    <div>
      <div role="tablist" aria-label="Content tabs">
        {tabs.map((tab, index) => (
          <button
            key={index}
            role="tab"
            aria-selected={activeIndex === index}
            aria-controls={`panel-${index}`}
            id={`tab-${index}`}
            tabIndex={activeIndex === index ? 0 : -1}
            onClick={() => setActiveIndex(index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map((tab, index) => (
        <div
          key={index}
          role="tabpanel"
          id={`panel-${index}`}
          aria-labelledby={`tab-${index}`}
          hidden={activeIndex !== index}
          tabIndex={0}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

Arrow keys navigate between tabs. Only the active tab is in the tab order (`tabIndex={0}`).

## ARIA Live Regions

```html
<!-- Polite: waits for screen reader to finish current announcement -->
<div aria-live="polite">New messages: 3</div>

<!-- Assertive: interrupts immediately (use sparingly) -->
<div aria-live="assertive" role="alert">Error: Form submission failed</div>
```

Use `aria-atomic="true"` to read the entire region on change. Use `polite` for non-critical updates, `assertive` for errors and critical alerts.

## Accessible Data Tables

```html
<table>
  <caption>
    Monthly sales by region
  </caption>
  <thead>
    <tr>
      <th scope="col">Region</th>
      <th scope="col">Q1</th>
      <th scope="col">Q2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">North</th>
      <td>$10,000</td>
      <td>$12,000</td>
    </tr>
  </tbody>
</table>
```

Use `<caption>` to describe the table, `scope="col"` and `scope="row"` to associate headers with data cells.
