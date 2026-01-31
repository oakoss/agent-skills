---
title: Server Components
description: React Server Components architecture, server/client boundary patterns, Server Actions for mutations, Suspense streaming, and data flow between server and client
tags:
  [
    server-components,
    server-actions,
    suspense,
    streaming,
    use-client,
    use-server,
    nextjs,
  ]
---

# Server Components

## Server-First Mental Model

Default to Server Components for everything. Add `'use client'` only at the leaves of the component tree where interactivity is needed. The root of the application is a Server Component that contains "islands" of Client Components.

```tsx
// app/dashboard/page.tsx -- Server Component (default)
import { Suspense } from 'react';
import { DashboardStats } from '@/components/features/dashboard-stats';
import { RecentActivity } from '@/components/features/recent-activity';
import { InteractiveChart } from '@/components/features/interactive-chart';

export default async function DashboardPage() {
  const stats = await fetchDashboardStats();

  return (
    <div className="space-y-6">
      <DashboardStats stats={stats} />
      <Suspense fallback={<ChartSkeleton />}>
        <InteractiveChart />
      </Suspense>
      <Suspense fallback={<ActivitySkeleton />}>
        <RecentActivity />
      </Suspense>
    </div>
  );
}
```

## Server vs Client Components

| Aspect                       | Server Component | Client Component                  |
| ---------------------------- | ---------------- | --------------------------------- |
| Directive                    | None (default)   | `'use client'` at top of file     |
| Runs on                      | Server only      | Server (SSR) + Client (hydration) |
| Can use hooks                | No               | Yes                               |
| Can use browser APIs         | No               | Yes                               |
| Can access DB/filesystem     | Yes              | No                                |
| Ships JS to client           | No               | Yes                               |
| Can render Server Components | Yes              | Only as `children` prop           |

## The Client Boundary

When you add `'use client'` to a file, all components imported into that file become part of the client bundle. Place the directive as deep in the tree as possible.

```tsx
// components/features/search-bar.tsx
'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';

export function SearchBar({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState('');

  return (
    <Input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === 'Enter') onSearch(query);
      }}
    />
  );
}
```

## Passing Server Components as Children

Client Components cannot import Server Components directly, but they can receive them as `children` or other React node props.

```tsx
// components/layouts/interactive-panel.tsx
'use client';

import { useState } from 'react';

interface InteractivePanelProps {
  children: React.ReactNode;
  sidebar: React.ReactNode;
}

export function InteractivePanel({ children, sidebar }: InteractivePanelProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="flex">
      {isOpen ? <aside className="w-64">{sidebar}</aside> : null}
      <button onClick={() => setIsOpen(!isOpen)}>Toggle</button>
      <main>{children}</main>
    </div>
  );
}
```

```tsx
// app/page.tsx -- Server Component composing client + server
import { InteractivePanel } from '@/components/layouts/interactive-panel';
import { ServerSidebar } from '@/components/features/server-sidebar';

export default async function Page() {
  const data = await fetchData();

  return (
    <InteractivePanel sidebar={<ServerSidebar />}>
      <div>{data.content}</div>
    </InteractivePanel>
  );
}
```

## Preventing Code Leakage

Use `server-only` and `client-only` packages to enforce boundaries at build time.

```tsx
// lib/db.ts
import 'server-only';

export async function getUsers() {
  return db.select().from(users);
}
```

```tsx
// lib/analytics.ts
import 'client-only';

export function trackEvent(name: string) {
  window.gtag('event', name);
}
```

## Server Actions

Server Actions allow Client Components to call server-side functions directly. They replace API routes for most mutation patterns.

### Inline Server Action

```tsx
// app/users/page.tsx
export default function UsersPage() {
  async function createUser(formData: FormData) {
    'use server';

    const name = formData.get('name') as string;
    await db.insert(users).values({ name });
    revalidatePath('/users');
  }

  return (
    <form action={createUser}>
      <input name="name" required />
      <button type="submit">Create User</button>
    </form>
  );
}
```

### Separate Actions File

```tsx
// app/users/actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

export async function createUser(formData: FormData) {
  const result = createUserSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
  });

  if (!result.success) {
    return { error: result.error.flatten().fieldErrors };
  }

  await db.insert(users).values(result.data);
  revalidatePath('/users');
  redirect('/users');
}
```

### Using Server Actions with useActionState

```tsx
// components/features/create-user-form.tsx
'use client';

import { useActionState } from 'react';
import { createUser } from '@/app/users/actions';

export function CreateUserForm() {
  const [state, formAction, isPending] = useActionState(createUser, null);

  return (
    <form action={formAction}>
      <input name="name" required />
      <input name="email" type="email" required />
      {state?.error ? (
        <p className="text-sm text-destructive">
          {JSON.stringify(state.error)}
        </p>
      ) : null}
      <button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
}
```

## Suspense Streaming

Wrap independent data-fetching sections in `<Suspense>` to stream UI progressively. Each boundary resolves independently.

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react';

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-2 gap-6">
      <Suspense fallback={<Skeleton className="h-48" />}>
        <RevenueChart />
      </Suspense>
      <Suspense fallback={<Skeleton className="h-48" />}>
        <UserGrowth />
      </Suspense>
      <Suspense fallback={<Skeleton className="h-64 col-span-2" />}>
        <RecentOrders />
      </Suspense>
    </div>
  );
}

async function RevenueChart() {
  const data = await fetchRevenue();
  return <Chart data={data} />;
}

async function UserGrowth() {
  const data = await fetchUserGrowth();
  return <Chart data={data} />;
}
```

## Optimistic Updates with Server Actions

```tsx
'use client';

import { useOptimistic } from 'react';
import { type Message } from '@/lib/types';
import { sendMessage } from '@/app/chat/actions';

export function MessageList({ messages }: { messages: Message[] }) {
  const [optimisticMessages, addOptimistic] = useOptimistic(
    messages,
    (state, newMessage: string) => [
      ...state,
      { id: 'temp', text: newMessage, sending: true },
    ],
  );

  async function handleSend(formData: FormData) {
    const text = formData.get('text') as string;
    addOptimistic(text);
    await sendMessage(formData);
  }

  return (
    <div>
      {optimisticMessages.map((msg) => (
        <div key={msg.id} className={msg.sending ? 'opacity-50' : ''}>
          {msg.text}
        </div>
      ))}
      <form action={handleSend}>
        <input name="text" required />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```
