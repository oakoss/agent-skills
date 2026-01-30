---
title: Recommended Libraries
description: Core stack, state management, forms, UI components, utilities, testing tools, and library selection criteria for React + TanStack projects
tags: [libraries, zustand, zod, shadcn, tailwind, vitest, playwright, msw, ky]
---

# Recommended Libraries

## Core Stack

```bash
# Foundation
pnpm add react react-dom
pnpm add @tanstack/react-query @tanstack/react-router

# TypeScript
pnpm add -D typescript @types/react @types/react-dom

# Build tool
pnpm add -D vite @vitejs/plugin-react
```

### Full-Stack Setup (TanStack Start)

```bash
pnpm create @tanstack/start my-app
cd my-app
pnpm add @tanstack/react-query zod drizzle-orm
```

## State Management

### Server State: TanStack Query (required)

```bash
pnpm add @tanstack/react-query
pnpm add -D @tanstack/react-query-devtools
```

### Client State: Zustand (not Redux)

```bash
pnpm add zustand
```

```ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIStore {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: 'light',
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setTheme: (theme) => set({ theme }),
    }),
    { name: 'ui-storage' },
  ),
);
```

Zustand over Redux: 90% less boilerplate, no providers needed, built-in persistence, simpler mental model, 2KB vs 40KB+.

## Forms and Validation

### Option A: TanStack Form (complex forms)

```bash
pnpm add @tanstack/react-form @tanstack/zod-form-adapter zod
```

### Option B: React Hook Form (mature, many integrations)

```bash
pnpm add react-hook-form @hookform/resolvers zod
```

### Validation: Zod (required)

```bash
pnpm add zod
```

```ts
import { z } from 'zod';

export const emailSchema = z.string().email('Invalid email');
export const passwordSchema = z
  .string()
  .min(8, 'Min 8 characters')
  .regex(/[A-Z]/, 'Need uppercase')
  .regex(/[0-9]/, 'Need number');

export const userSchema = z.object({
  name: z.string().min(2).max(100),
  email: emailSchema,
  age: z.number().min(0).max(150).optional(),
});

export type User = z.infer<typeof userSchema>;
```

## UI Components

### Option A: Shadcn/ui (recommended)

```bash
pnpm dlx shadcn-ui@latest init
pnpm dlx shadcn-ui@latest add button input card
```

Copy-paste (not a dependency), full control, Radix primitives (accessible), Tailwind styling.

### Styling: Tailwind CSS

```bash
pnpm add -D tailwindcss postcss autoprefixer
pnpm add tailwind-merge clsx
```

```ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### Icons: Lucide React

```bash
pnpm add lucide-react
```

## Utilities

### Date Handling: date-fns

```bash
pnpm add date-fns
```

### HTTP Client: ky or axios

```bash
pnpm add ky    # Lightweight (6KB)
pnpm add axios # Full-featured (30KB)
```

```ts
import ky from 'ky';

export const api = ky.create({
  prefixUrl: '/api',
  timeout: 30000,
  hooks: {
    beforeRequest: [
      (request) => {
        const token = getToken();
        if (token) request.headers.set('Authorization', `Bearer ${token}`);
      },
    ],
  },
});
```

### Environment Variables: @t3-oss/env-core

```bash
pnpm add @t3-oss/env-core zod
```

```ts
import { createEnv } from '@t3-oss/env-core';
import { z } from 'zod';

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
    JWT_SECRET: z.string().min(32),
  },
  client: {
    NEXT_PUBLIC_API_URL: z.string().url(),
  },
  runtimeEnv: process.env,
});
```

## Testing

### Unit Testing: Vitest

```bash
pnpm add -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

### E2E Testing: Playwright

```bash
pnpm add -D @playwright/test
pnpm exec playwright install
```

### API Mocking: MSW

```bash
pnpm add -D msw
```

```ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([{ id: '1', name: 'John' }]);
  }),
];
```

## Library Selection Criteria

| Criterion          | Threshold                           |
| ------------------ | ----------------------------------- |
| Bundle size        | Acceptable (check bundlephobia.com) |
| TypeScript support | First-class                         |
| Active maintenance | Last commit under 3 months ago      |
| Downloads          | Over 10k/week for production use    |
| Documentation      | Comprehensive                       |
| Escape hatch       | No vendor lock-in                   |

## Library Comparison

| Need          | Recommended         | Avoid                  |
| ------------- | ------------------- | ---------------------- |
| Server state  | TanStack Query      | SWR (fewer features)   |
| Client state  | Zustand             | Redux (overkill)       |
| Routing       | TanStack Router     | React Router v5        |
| Forms         | RHF / TanStack Form | Formik (outdated)      |
| Validation    | Zod                 | Yup (worse TS)         |
| UI Components | Shadcn/ui           | Material UI (heavy)    |
| Styling       | Tailwind            | Styled-components      |
| Date          | date-fns            | Moment.js (deprecated) |
| HTTP          | ky / axios          | custom fetch wrapper   |
| Testing       | Vitest              | Jest (slower)          |
| E2E           | Playwright          | Cypress (slower)       |
