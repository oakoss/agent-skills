---
title: Component Architecture
description: Component types (Page, Feature, UI, Layout), folder structure for Next.js App Router, TypeScript prop patterns, and composition strategies
tags: [components, react, nextjs, typescript, folder-structure, composition]
---

# Component Architecture

## Component Types

### Page Components

Route entry points that compose feature and layout components. In Next.js App Router, these are Server Components by default.

```tsx
// app/users/page.tsx
import { UserList } from '@/components/features/user-list';

export default async function UsersPage() {
  const users = await fetchUsers();

  return (
    <main className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Users</h1>
      <UserList users={users} />
    </main>
  );
}
```

### Feature Components

Contain business logic and data handling. Compose UI components together for a specific use case.

```tsx
// components/features/user-list.tsx
'use client';

import { useState } from 'react';
import { type User } from '@/lib/types';
import { UserCard } from '@/components/ui/user-card';
import { Input } from '@/components/ui/input';

interface UserListProps {
  users: User[];
}

export function UserList({ users }: UserListProps) {
  const [search, setSearch] = useState('');

  const filtered = users.filter((user) =>
    user.name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="space-y-4">
      <Input
        placeholder="Search users..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filtered.map((user) => (
          <UserCard key={user.id} user={user} />
        ))}
      </div>
    </div>
  );
}
```

### UI Components

Reusable, stateless presentation components with no business logic. These map to shadcn/ui primitives or custom design system atoms.

```tsx
// components/ui/user-card.tsx
import { type User } from '@/lib/types';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

interface UserCardProps {
  user: User;
}

export function UserCard({ user }: UserCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-3">
        <Avatar>
          <AvatarImage src={user.avatar} alt={user.name} />
          <AvatarFallback>{user.name[0]}</AvatarFallback>
        </Avatar>
        <div>
          <p className="font-medium">{user.name}</p>
          <p className="text-sm text-muted-foreground">{user.email}</p>
        </div>
      </CardHeader>
    </Card>
  );
}
```

### Layout Components

Structural components for page chrome: headers, sidebars, footers.

```tsx
// components/layouts/sidebar-layout.tsx
interface SidebarLayoutProps {
  sidebar: React.ReactNode;
  children: React.ReactNode;
}

export function SidebarLayout({ sidebar, children }: SidebarLayoutProps) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r bg-muted/50">{sidebar}</aside>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
```

## TypeScript Prop Patterns

### Typed Props with Defaults

```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  children,
  onClick,
}: ButtonProps) {
  return (
    <button disabled={disabled} onClick={onClick}>
      {children}
    </button>
  );
}
```

### Extending HTML Elements

```tsx
import { type ComponentPropsWithoutRef } from 'react';

interface InputProps extends ComponentPropsWithoutRef<'input'> {
  label: string;
  error?: string;
}

export function Input({ label, error, className, ...props }: InputProps) {
  return (
    <div>
      <label className="text-sm font-medium">{label}</label>
      <input className={cn('border rounded px-3 py-2', className)} {...props} />
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
    </div>
  );
}
```

### Discriminated Union Props

```tsx
type NotificationProps =
  | { variant: 'success'; message: string }
  | { variant: 'error'; message: string; retry: () => void }
  | { variant: 'loading' };

export function Notification(props: NotificationProps) {
  switch (props.variant) {
    case 'success':
      return <div className="text-green-600">{props.message}</div>;
    case 'error':
      return (
        <div className="text-red-600">
          {props.message}
          <button onClick={props.retry}>Retry</button>
        </div>
      );
    case 'loading':
      return <div className="animate-pulse">Loading...</div>;
  }
}
```

## Folder Structure (Next.js App Router)

```sh
app/
├── (auth)/              # Route group (no URL segment)
│   ├── login/page.tsx
│   └── signup/page.tsx
├── (dashboard)/
│   ├── layout.tsx       # Shared dashboard layout
│   ├── page.tsx
│   └── settings/page.tsx
├── api/                 # Route Handlers
│   └── users/route.ts
├── error.tsx            # Root error boundary
├── loading.tsx          # Root loading UI
├── layout.tsx           # Root layout
└── page.tsx             # Home page

components/
├── ui/                  # shadcn/ui primitives
│   ├── button.tsx
│   ├── input.tsx
│   └── dialog.tsx
├── features/            # Business logic components
│   ├── user-list.tsx
│   └── user-profile.tsx
└── layouts/             # Page structure
    ├── header.tsx
    └── sidebar.tsx

lib/
├── utils.ts             # cn() and shared utilities
├── api.ts               # API client configuration
└── schemas.ts           # Shared Zod schemas

hooks/
├── use-debounce.ts
└── use-media-query.ts

stores/
└── user-store.ts        # Zustand stores
```

## Composition Patterns

### Compound Components

```tsx
function Tabs({ children }: { children: React.ReactNode }) {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div>{children}</div>
    </TabsContext.Provider>
  );
}

function TabList({ children }: { children: React.ReactNode }) {
  return (
    <div role="tablist" className="flex border-b">
      {children}
    </div>
  );
}

function TabPanel({
  index,
  children,
}: {
  index: number;
  children: React.ReactNode;
}) {
  const { activeTab } = useTabsContext();
  return activeTab === index ? <div role="tabpanel">{children}</div> : null;
}

Tabs.List = TabList;
Tabs.Panel = TabPanel;
```

### Render Props (Headless Components)

```tsx
interface DataListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  emptyState?: React.ReactNode;
}

export function DataList<T>({
  items,
  renderItem,
  emptyState,
}: DataListProps<T>) {
  if (items.length === 0) {
    return <>{emptyState ?? <p>No items found.</p>}</>;
  }

  return <div className="space-y-2">{items.map(renderItem)}</div>;
}
```
