---
title: Data Fetching
description: TanStack Query for client-side fetching with queries and mutations, and Next.js Server Components for server-side data fetching
tags: [data-fetching, tanstack-query, server-components, nextjs, react-query]
---

# Data Fetching

## TanStack Query

### Query (GET)

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

function Users() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
    staleTime: 5 * 60 * 1000 // 5 minutes
  })

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />

  return <UserList users={data} />
}
```

### Mutation (POST, PUT, DELETE)

```typescript
function CreateUser() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })

  return (
    <button onClick={() => mutation.mutate({ name: 'John' })}>
      Create User
    </button>
  )
}
```

## Next.js Server Components

```typescript
// app/users/page.tsx
// Server Component - fetches on server
export default async function UsersPage() {
  const users = await fetchUsers() // Runs on server

  return <UserList users={users} />
}

// Client Component - for interactivity
'use client'

export function UserList({ users }: { users: User[] }) {
  const [selected, setSelected] = useState<string | null>(null)

  return (
    <div>
      {users.map(user => (
        <UserCard
          key={user.id}
          user={user}
          onClick={() => setSelected(user.id)}
        />
      ))}
    </div>
  )
}
```
