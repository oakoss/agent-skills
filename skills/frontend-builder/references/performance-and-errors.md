---
title: Performance and Errors
description: React memoization patterns (useMemo, useCallback, memo), Next.js image/font/code-splitting optimization, and error boundary implementation
tags:
  [
    performance,
    memoization,
    error-boundary,
    nextjs-optimization,
    code-splitting,
  ]
---

# Performance and Errors

## React Memoization

```typescript
import { memo, useMemo, useCallback } from 'react'

// 1. Memoize expensive calculations
function DataTable({ data }) {
  const sortedData = useMemo(
    () => data.sort((a, b) => a.name.localeCompare(b.name)),
    [data]
  )

  return <Table data={sortedData} />
}

// 2. Memoize callbacks
function Parent() {
  const handleClick = useCallback(() => {
    console.log('Clicked')
  }, [])

  return <ExpensiveChild onClick={handleClick} />
}

// 3. Memoize components
const ExpensiveChild = memo(function ExpensiveChild({ onClick }) {
  return <button onClick={onClick}>Click</button>
})
```

## Next.js Optimization

```typescript
// 1. Image optimization
import Image from 'next/image'

<Image
  src="/photo.jpg"
  alt="Photo"
  width={500}
  height={300}
  priority // Above the fold
/>

// 2. Font optimization
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }) {
  return (
    <html className={inter.className}>
      <body>{children}</body>
    </html>
  )
}

// 3. Dynamic imports (code splitting)
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />
})
```

## Error Boundary

```typescript
'use client'

import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 bg-red-50 border border-red-200">
          <h2 className="text-red-800">Something went wrong</h2>
          <p className="text-red-600">{this.state.error?.message}</p>
        </div>
      )
    }

    return this.props.children
  }
}
```

## Next.js Error Page

```typescript
// app/error.tsx
'use client'

export default function Error({
  error,
  reset
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

## TypeScript Best Practices

```typescript
// 1. Type component props
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger'
  children: ReactNode
  onClick?: () => void
}

export function Button({ variant = 'primary', children, onClick }: ButtonProps) {
  return <button onClick={onClick}>{children}</button>
}

// 2. Type API responses
interface User {
  id: string
  name: string
  email: string
}

async function fetchUsers(): Promise<User[]> {
  const res = await fetch('/api/users')
  return res.json()
}

// 3. Type state
const [user, setUser] = useState<User | null>(null)
const [isLoading, setIsLoading] = useState<boolean>(false)
```
