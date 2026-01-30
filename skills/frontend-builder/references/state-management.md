---
title: State Management
description: Local state with useState, app-wide state with Context API, and complex state with Zustand including decision tree
tags: [state, useState, context, zustand, react]
---

# State Management

## Decision Tree

```text
How many components need this state?
│
├─ One component → useState
├─ Parent + children → Props or useState + props
├─ Siblings → Lift to common parent
├─ Widely used (theme, auth) → Context API
└─ Complex app state → Zustand or Redux
```

## Local State (useState)

```typescript
function Counter() {
  const [count, setCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>{count}</button>
    </div>
  )
}
```

## Context API

```typescript
const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) throw new Error('useUser must be within UserProvider')
  return context
}
```

## Zustand (Complex State)

```typescript
import { create } from 'zustand'

interface CounterStore {
  count: number
  increment: () => void
  decrement: () => void
  reset: () => void
}

export const useCounterStore = create<CounterStore>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 })
}))

// Usage
function Counter() {
  const { count, increment } = useCounterStore()
  return <button onClick={increment}>{count}</button>
}
```
