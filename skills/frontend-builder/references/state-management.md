---
title: State Management
description: State management decision tree covering useState, Context API, Zustand, and URL state with nuqs for React and Next.js applications
tags: [state, useState, context, zustand, url-state, nuqs, react]
---

# State Management

## Decision Tree

| Scope                         | Solution                    | When to Use                               |
| ----------------------------- | --------------------------- | ----------------------------------------- |
| Single component              | `useState`                  | Toggle, input value, local UI state       |
| Parent + children             | Props drilling              | 1-2 levels deep                           |
| Siblings                      | Lift state to common parent | Shared state between adjacent components  |
| App-wide (infrequent updates) | Context API                 | Theme, auth, locale                       |
| Complex client state          | Zustand                     | Shopping cart, multi-step wizard, filters |
| Shareable/bookmarkable        | URL search params           | Pagination, filters, tabs, sort order     |
| Server state                  | TanStack Query              | API data with caching and revalidation    |

## Local State (useState)

```tsx
function TogglePanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'info' | 'settings'>('info');

  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? 'Collapse' : 'Expand'}
      </button>
      {isOpen ? (
        <div>
          <div className="flex gap-2">
            <button onClick={() => setActiveTab('info')}>Info</button>
            <button onClick={() => setActiveTab('settings')}>Settings</button>
          </div>
          {activeTab === 'info' ? <InfoPanel /> : <SettingsPanel />}
        </div>
      ) : null}
    </div>
  );
}
```

### Derived State (No Extra useState)

```tsx
function UserList({ users }: { users: User[] }) {
  const [search, setSearch] = useState('');

  const filteredUsers = useMemo(
    () =>
      users.filter((u) => u.name.toLowerCase().includes(search.toLowerCase())),
    [users, search],
  );

  const userCount = filteredUsers.length;

  return (
    <div>
      <Input value={search} onChange={(e) => setSearch(e.target.value)} />
      <p>{userCount} users found</p>
      {filteredUsers.map((user) => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

## Context API

Best for infrequently changing values (theme, auth, locale). Avoid for state that updates frequently since all consumers re-render on every change.

```tsx
// providers/theme-provider.tsx
'use client';

import { createContext, useContext, useState, type ReactNode } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');

  const toggleTheme = () => setTheme((t) => (t === 'light' ? 'dark' : 'light'));

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

### Context with Reducer (Complex Updates)

```tsx
'use client';

import { createContext, useContext, useReducer, type ReactNode } from 'react';

interface AuthState {
  user: User | null;
  isLoading: boolean;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; user: User }
  | { type: 'LOGOUT' };

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true };
    case 'LOGIN_SUCCESS':
      return { user: action.user, isLoading: false };
    case 'LOGOUT':
      return { user: null, isLoading: false };
  }
}

const AuthContext = createContext<
  | {
      state: AuthState;
      dispatch: React.Dispatch<AuthAction>;
    }
  | undefined
>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    isLoading: false,
  });

  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

## Zustand (Complex Client State)

Zustand provides a lightweight store that works outside React's component tree. Use selectors to prevent unnecessary re-renders.

```tsx
// stores/cart-store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

interface CartStore {
  items: CartItem[];
  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clearCart: () => void;
  total: () => number;
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      addItem: (item) =>
        set((state) => {
          const existing = state.items.find((i) => i.id === item.id);
          if (existing) {
            return {
              items: state.items.map((i) =>
                i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i,
              ),
            };
          }
          return { items: [...state.items, { ...item, quantity: 1 }] };
        }),
      removeItem: (id) =>
        set((state) => ({ items: state.items.filter((i) => i.id !== id) })),
      updateQuantity: (id, quantity) =>
        set((state) => ({
          items: state.items.map((i) => (i.id === id ? { ...i, quantity } : i)),
        })),
      clearCart: () => set({ items: [] }),
      total: () =>
        get().items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    }),
    { name: 'cart-storage' },
  ),
);
```

### Using Selectors

```tsx
function CartCount() {
  const itemCount = useCartStore((state) => state.items.length);
  return <span className="badge">{itemCount}</span>;
}

function CartTotal() {
  const total = useCartStore((state) => state.total());
  return <span>${total.toFixed(2)}</span>;
}
```

## URL State

Use URL search params for state that should be shareable, bookmarkable, or survive page refreshes. The `nuqs` library provides type-safe URL state management for Next.js.

```tsx
'use client';

import { useQueryState, parseAsInteger, parseAsStringEnum } from 'nuqs';

const sortOptions = ['name', 'date', 'price'] as const;

export function ProductFilters() {
  const [search, setSearch] = useQueryState('q', { defaultValue: '' });
  const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
  const [sort, setSort] = useQueryState(
    'sort',
    parseAsStringEnum(sortOptions).withDefault('name'),
  );

  return (
    <div className="flex gap-4">
      <Input value={search} onChange={(e) => setSearch(e.target.value)} />
      <Select value={sort} onValueChange={setSort}>
        {sortOptions.map((opt) => (
          <SelectItem key={opt} value={opt}>
            {opt}
          </SelectItem>
        ))}
      </Select>
      <Pagination page={page} onPageChange={setPage} />
    </div>
  );
}
```
