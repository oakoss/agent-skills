---
title: Component Architecture
description: Page, feature, and UI component patterns with TypeScript typing, component best practices, and folder structure for Next.js App Router
tags: [components, react, nextjs, typescript, folder-structure]
---

# Component Architecture

## Page Components

```typescript
// app/users/page.tsx (Next.js App Router)
export default function UsersPage() {
  return (
    <div>
      <Header />
      <UserList />
      <Footer />
    </div>
  )
}
```

## Feature Components

```typescript
// components/features/UserList.tsx
export function UserList() {
  const { data, isLoading } = useUsers()

  if (isLoading) return <LoadingSpinner />

  return (
    <div>
      {data.map(user => <UserCard key={user.id} user={user} />)}
    </div>
  )
}
```

## UI Components

```typescript
// components/ui/button.tsx
export function Button({ children, variant = 'primary', ...props }) {
  return (
    <button
      className={cn(buttonVariants[variant])}
      {...props}
    >
      {children}
    </button>
  )
}
```

## Component Best Practices

```typescript
// Small, focused, typed
interface UserProfileProps {
  user: User
  onEdit?: () => void
}

export function UserProfile({ user, onEdit }: UserProfileProps) {
  return (
    <div className="flex gap-4">
      <Avatar src={user.avatar} alt={user.name} />
      <UserDetails user={user} />
      {onEdit && <Button onClick={onEdit}>Edit</Button>}
    </div>
  )
}
```

## Folder Structure

```sh
app/
├── (auth)/              # Route group (auth pages)
│   ├── login/
│   └── signup/
├── (dashboard)/         # Route group (dashboard)
│   ├── layout.tsx
│   ├── page.tsx
│   └── settings/
├── api/                 # API routes
│   └── users/
│       └── route.ts
└── layout.tsx           # Root layout

components/
├── ui/                  # shadcn/ui components
│   ├── button.tsx
│   ├── input.tsx
│   └── dialog.tsx
├── features/            # Feature components
│   ├── UserList.tsx
│   └── UserProfile.tsx
└── layouts/             # Layout components
    ├── Header.tsx
    └── Footer.tsx

lib/
├── utils.ts             # Utility functions
├── api.ts               # API client
└── validation.ts        # Zod schemas

hooks/
├── useUser.ts
└── useDebounce.ts

stores/
└── userStore.ts         # Zustand stores
```
