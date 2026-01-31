---
title: Code Splitting
description: React.lazy, Suspense, dynamic imports, barrel file avoidance, bundle size optimization, preloading, and conditional module loading
tags:
  [
    lazy,
    suspense,
    dynamic-import,
    code-splitting,
    bundle,
    barrel-files,
    preload,
    tree-shaking,
  ]
---

# Code Splitting

## React.lazy with Suspense

Lazy-load heavy components that are not needed on initial render:

```tsx
import { lazy, Suspense } from 'react';

const MonacoEditor = lazy(() =>
  import('./monaco-editor').then((m) => ({ default: m.MonacoEditor })),
);

function CodePanel({ code }: { code: string }) {
  return (
    <Suspense fallback={<div>Loading editor...</div>}>
      <MonacoEditor value={code} />
    </Suspense>
  );
}
```

The `.then()` wrapper is needed when the module does not have a default export.

## Route-Based Splitting

Split at route boundaries for the most impactful code splitting:

```tsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/dashboard'));
const Settings = lazy(() => import('./pages/settings'));
const Analytics = lazy(() => import('./pages/analytics'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
}
```

Each route loads its own chunk. Users only download code for the page they visit.

## Preload on User Intent

Trigger `import()` on hover or focus to preload chunks before the user clicks:

```tsx
function EditorButton({ onClick }: { onClick: () => void }) {
  const preload = () => {
    if (typeof window !== 'undefined') {
      void import('./monaco-editor');
    }
  };

  return (
    <button onMouseEnter={preload} onFocus={preload} onClick={onClick}>
      Open Editor
    </button>
  );
}
```

The browser caches the import, so the component loads instantly when activated.

## Preload on Feature Flag

Start loading modules when a feature is enabled, not when the UI needs them:

```tsx
function FlagsProvider({ children, flags }: Props) {
  useEffect(() => {
    if (flags.editorEnabled && typeof window !== 'undefined') {
      void import('./monaco-editor').then((mod) => mod.init());
    }
  }, [flags.editorEnabled]);

  return (
    <FlagsContext.Provider value={flags}>{children}</FlagsContext.Provider>
  );
}
```

## Conditional Module Loading

Load large data modules only when a feature is activated:

```tsx
function AnimationPlayer({
  enabled,
  setEnabled,
}: {
  enabled: boolean;
  setEnabled: React.Dispatch<React.SetStateAction<boolean>>;
}) {
  const [frames, setFrames] = useState<Frame[] | null>(null);

  useEffect(() => {
    if (enabled && !frames && typeof window !== 'undefined') {
      import('./animation-frames.js')
        .then((mod) => setFrames(mod.frames))
        .catch(() => setEnabled(false));
    }
  }, [enabled, frames, setEnabled]);

  if (!frames) return <Skeleton />;
  return <Canvas frames={frames} />;
}
```

The `typeof window !== 'undefined'` check prevents bundling the module for SSR.

## Avoid Barrel File Imports

Barrel files (index files that re-export everything) force bundlers to load thousands of unused modules:

```tsx
import Check from 'lucide-react/dist/esm/icons/check';
import X from 'lucide-react/dist/esm/icons/x';
import Menu from 'lucide-react/dist/esm/icons/menu';
```

Libraries commonly affected: `lucide-react`, `@mui/material`, `@mui/icons-material`, `@tabler/icons-react`, `react-icons`, `lodash`, `date-fns`.

Direct imports provide 15-70% faster dev boot, 28% faster builds, and 40% faster cold starts.

### Next.js optimizePackageImports

Next.js 13.5+ can automatically transform barrel imports at build time:

```js
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@mui/material'],
  },
};
```

With this configured, ergonomic barrel imports are safe:

```tsx
import { Check, X, Menu } from 'lucide-react';
```

## Defer Third-Party Libraries

Load analytics, logging, and tracking after hydration to keep the critical path lean:

```tsx
import { useEffect, useState, lazy, Suspense } from 'react';

const Analytics = lazy(() =>
  import('@vercel/analytics/react').then((m) => ({ default: m.Analytics })),
);

export default function App({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div>
      {children}
      {mounted ? (
        <Suspense fallback={null}>
          <Analytics />
        </Suspense>
      ) : null}
    </div>
  );
}
```

## Suspense Boundaries for Streaming

Place Suspense boundaries around async Server Components to stream content progressively:

```tsx
function Page() {
  return (
    <div>
      <Sidebar />
      <Header />
      <Suspense fallback={<Skeleton />}>
        <DataDisplay />
      </Suspense>
      <Footer />
    </div>
  );
}

async function DataDisplay() {
  const data = await fetchData();
  return <div>{data.content}</div>;
}
```

Static content renders immediately while data-dependent sections stream in as they resolve.

## Bundle Analysis Checklist

When auditing bundle size, check for these common issues:

1. **Barrel file imports** -- switch to direct imports or configure `optimizePackageImports`
2. **Undeferred third-party scripts** -- analytics, error tracking, chat widgets
3. **Large components in initial bundle** -- code editors, charts, maps, PDF viewers
4. **Duplicate dependencies** -- multiple versions of the same library
5. **Unused exports** -- dead code that bundlers cannot tree-shake due to side effects
6. **Polyfills for modern browsers** -- unnecessary compatibility code
