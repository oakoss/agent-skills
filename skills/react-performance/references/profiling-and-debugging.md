---
title: Profiling and Debugging
description: React DevTools Profiler, performance measurement, bundle analysis, identifying re-render causes, and common performance bottlenecks
tags:
  [
    profiler,
    devtools,
    debugging,
    re-renders,
    bundle-analyzer,
    performance,
    flamegraph,
    why-did-you-render,
  ]
---

# Profiling and Debugging

## React DevTools Profiler

The Profiler tab in React DevTools records component renders and measures their duration.

### Recording a Profile

1. Open React DevTools and switch to the **Profiler** tab
2. Click **Record** (blue circle)
3. Perform the interaction you want to measure
4. Click **Stop** to end recording

### Reading the Flamegraph

The flamegraph shows the component tree for each commit (render):

- **Gray bars** -- components that did not render in this commit
- **Colored bars** -- components that rendered; color intensity indicates render duration
- **Width** -- relative render time compared to siblings
- **Hover** -- shows exact render time and reason for re-render

### Identifying Slow Components

Sort by render duration to find the most expensive components:

```text
Profiler > Ranked chart > Sort by self time
```

Components with high self time are doing expensive work during render. Common causes:

- Large list rendering without virtualization
- Expensive computations not wrapped in `useMemo`
- Creating new objects/arrays on every render
- Calling expensive functions during render instead of memoizing results

### Identifying Unnecessary Re-renders

Enable "Record why each component rendered" in Profiler settings:

```text
Profiler > Settings (gear icon) > Record why each component rendered
```

Common re-render reasons:

- **Props changed** -- parent passes new object references; check if the values actually changed
- **State changed** -- expected re-render; verify the state change is necessary
- **Context changed** -- context value creates new reference; split contexts or memoize the value
- **Parent rendered** -- wrap child in `React.memo` if its props are stable

## Highlight Updates

Enable visual re-render indicators to spot unnecessary renders in real time:

```text
React DevTools > Settings > General > Highlight updates when components render
```

Components flash colored borders when they re-render. Frequent flashing on components that should be static indicates optimization opportunities.

## React Compiler DevTools

When React Compiler is enabled, DevTools shows optimization status:

- **"Memo" badge** on components -- the compiler successfully memoized the component
- **No badge** -- the compiler skipped optimization; check for Rules of React violations

Use the `react-compiler-healthcheck` CLI to audit your codebase:

```bash
npx react-compiler-healthcheck@latest
```

This reports how many components the compiler can optimize and which ones it skips.

## Production Profiling

Development mode includes extra warnings, strict mode double-renders, and debugging aids that distort performance measurements. Always profile production builds.

### Next.js Production Profiling

```bash
next build --profile
```

This creates a production build with profiling enabled. Then use React DevTools Profiler as normal.

### Vite/CRA Production Profiling

Add the profiling bundle alias to the production build:

```ts
// vite.config.ts
export default defineConfig({
  resolve: {
    alias: {
      'react-dom$': 'react-dom/profiling',
      'scheduler/tracing': 'scheduler/tracing-profiling',
    },
  },
});
```

Build and serve the production bundle, then profile with React DevTools.

## Bundle Analysis

Visualize what is in your JavaScript bundles to find optimization targets.

### Next.js Bundle Analyzer

```bash
pnpm add -D @next/bundle-analyzer
```

```js
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({});
```

```bash
ANALYZE=true next build
```

Opens an interactive treemap showing chunk composition. Look for:

- Unexpectedly large dependencies
- Duplicate packages (multiple versions)
- Libraries that should be code-split

### Vite Bundle Analysis

```bash
pnpm add -D rollup-plugin-visualizer
```

```ts
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [visualizer({ open: true, gzipSize: true })],
});
```

### Source Map Explorer

Framework-agnostic tool that works with any source maps:

```bash
npx source-map-explorer dist/assets/*.js
```

## Performance Measurement in Code

Use the React Profiler component for programmatic performance tracking:

```tsx
import { Profiler, type ProfilerOnRenderCallback } from 'react';

const onRender: ProfilerOnRenderCallback = (
  id,
  phase,
  actualDuration,
  baseDuration,
  startTime,
  commitTime,
) => {
  if (actualDuration > 16) {
    console.warn(`Slow render: ${id} took ${actualDuration.toFixed(1)}ms`);
  }
};

function App() {
  return (
    <Profiler id="Dashboard" onRender={onRender}>
      <Dashboard />
    </Profiler>
  );
}
```

The 16ms threshold corresponds to 60fps. Components exceeding this cause visible jank.

## Common Bottleneck Patterns

### Large List Without Virtualization

Rendering thousands of DOM nodes causes slow initial render and expensive re-renders:

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualItem.start}px)`,
              height: `${virtualItem.size}px`,
              width: '100%',
            }}
          >
            <ItemRow item={items[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

Virtualization renders only visible items. For 10,000 items, only ~20 DOM nodes exist at any time.

### Context Re-render Cascade

A single context value change re-renders all consumers:

```tsx
const ThemeContext = createContext<Theme>(defaultTheme);
const UserContext = createContext<User | null>(null);

function AppProviders({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(defaultTheme);
  const [user, setUser] = useState<User | null>(null);

  return (
    <ThemeContext.Provider value={theme}>
      <UserContext.Provider value={user}>{children}</UserContext.Provider>
    </ThemeContext.Provider>
  );
}
```

Split contexts by update frequency. Components consuming `ThemeContext` do not re-render when `user` changes.

### Expensive Render in Unrelated Update

State colocation prevents unrelated components from re-rendering:

```tsx
function SearchSection() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Result[]>([]);

  return (
    <div>
      <SearchInput query={query} onChange={setQuery} />
      <SearchResults results={results} />
    </div>
  );
}

function Page() {
  return (
    <div>
      <SearchSection />
      <ExpensiveChart />
    </div>
  );
}
```

By colocating `query` state inside `SearchSection`, typing in the search input does not re-render `ExpensiveChart`.

## Optimization Priority

When optimizing a React application, prioritize by impact:

1. **Eliminate data fetching waterfalls** -- parallel fetches, Suspense streaming (CRITICAL)
2. **Reduce bundle size** -- code splitting, direct imports, deferred third-party (CRITICAL)
3. **Fix re-render cascades** -- context splitting, state colocation, memoization (MEDIUM)
4. **Optimize rendering** -- virtualization, content-visibility, transitions (MEDIUM)
5. **JavaScript micro-optimizations** -- loop combining, Set/Map lookups (LOW)

Start from the top. Lower-priority optimizations rarely matter if higher-priority issues exist.
