---
title: Hooks and Server Actions
description: React 19 use() API, useActionState, useOptimistic, useTransition, useEffectEvent, and useId patterns
tags:
  [
    hooks,
    use,
    useActionState,
    useOptimistic,
    useTransition,
    useEffectEvent,
    useId,
    server-actions,
    forms,
  ]
---

# Hooks and Server Actions

## The `use()` API (React 19)

Replaces the `useEffect` + `useState` fetch pattern. Unwraps promises or context values within the render body. Must be used inside a Suspense boundary when reading promises.

```tsx
// Bad: The old useEffect boilerplate
function Profile({ id }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetchData(id).then(setData);
  }, [id]);
  if (!data) return <Loading />;
  return <div>{data.name}</div>;
}

// Good: Using use() with Suspense
import { use } from 'react';

function Profile({ dataPromise }) {
  const data = use(dataPromise);
  return <div>{data.name}</div>;
}
```

### Sharing Promises Across Components

```tsx
function Page() {
  const dataPromise = fetchData();
  return (
    <div>
      <Suspense fallback={<Skeleton />}>
        <DataDisplay dataPromise={dataPromise} />
        <DataSummary dataPromise={dataPromise} />
      </Suspense>
    </div>
  );
}

function DataDisplay({ dataPromise }: { dataPromise: Promise<Data> }) {
  const data = use(dataPromise);
  return <div>{data.content}</div>;
}

function DataSummary({ dataPromise }: { dataPromise: Promise<Data> }) {
  const data = use(dataPromise);
  return <div>{data.summary}</div>;
}
```

Both components share the same promise, so only one fetch occurs.

### Reading Context with use()

`use()` can also read context, replacing `useContext`. Unlike `useContext`, it can be called conditionally:

```tsx
import { use } from 'react';

function StatusIcon({ isLoggedIn }: { isLoggedIn: boolean }) {
  if (isLoggedIn) {
    const theme = use(ThemeContext);
    return <Icon color={theme.primary} />;
  }
  return <Icon color="gray" />;
}
```

## `useActionState` (Form Management)

Built-in pending states and error states for forms with Server Actions:

```tsx
import { useActionState } from 'react';
import { updateProfile } from './actions';

function ProfileForm() {
  const [state, action, isPending] = useActionState(updateProfile, {
    message: null,
  });

  return (
    <form action={action}>
      <input name="username" disabled={isPending} />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Saving...' : 'Save'}
      </button>
      {state.message ? <p>{state.message}</p> : null}
    </form>
  );
}
```

### Server Action Pattern

```tsx
'use server';

export async function updateProfile(
  prevState: { message: string | null },
  formData: FormData,
) {
  const username = formData.get('username');
  if (!username) {
    return { message: 'Username is required' };
  }
  await db.user.update({ where: { id: session.userId }, data: { username } });
  return { message: 'Profile updated' };
}
```

## `useOptimistic` (Instant UI Feedback)

Show temporary state while an async action is in flight:

```tsx
import { useOptimistic, useRef, startTransition } from 'react';

function ChatList({
  messages,
  sendMessage,
}: {
  messages: Message[];
  sendMessage: (formData: FormData) => Promise<void>;
}) {
  const formRef = useRef<HTMLFormElement>(null);
  const [optimisticMessages, addOptimisticMessage] = useOptimistic(
    messages,
    (state, newMessage: string) => [
      ...state,
      { text: newMessage, sending: true },
    ],
  );

  function formAction(formData: FormData) {
    const text = formData.get('message') as string;
    addOptimisticMessage(text);
    formRef.current?.reset();
    startTransition(async () => {
      await sendMessage(formData);
    });
  }

  return (
    <div>
      {optimisticMessages.map((m, i) => (
        <div key={i}>
          {m.text}
          {m.sending ? <small> (Sending...)</small> : null}
        </div>
      ))}
      <form action={formAction} ref={formRef}>
        <input name="message" />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

## `useTransition` (Non-Urgent Updates)

Mark non-urgent updates as interruptible for responsive UI:

```tsx
const [isPending, startTransition] = useTransition();

const handleSearch = (query: string) => {
  setQuery(query); // urgent: update input immediately

  startTransition(() => {
    setFilteredResults(filterItems(query)); // non-urgent: can be interrupted
  });
};
```

### Calling Server Functions with Transitions

```tsx
'use client';

import { useState, useTransition } from 'react';
import { updateName } from './actions';

function UpdateName() {
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const submitAction = () => {
    startTransition(async () => {
      const result = await updateName(name);
      if (result.error) {
        setError(result.error);
      } else {
        setName('');
      }
    });
  };

  return (
    <form action={submitAction}>
      <input type="text" name="name" disabled={isPending} />
      {error ? <span>Failed: {error}</span> : null}
    </form>
  );
}
```

## `useEffectEvent` (React 19.2)

For logic that depends on reactive values but should not trigger the effect. Stable in React 19.2+, replacing the old `useRef` workaround pattern.

```tsx
import { useEffect, useEffectEvent } from 'react';

function Chat({ roomId, theme }: { roomId: string; theme: string }) {
  const onConnected = useEffectEvent(() => {
    logAnalytics('Connected', { theme }); // reads latest theme
  });

  useEffect(() => {
    const socket = connect(roomId);
    socket.on('connect', onConnected);
    return () => socket.disconnect();
  }, [roomId]); // theme is NOT a dependency
}
```

Rules for `useEffectEvent`:

- Call at the top level of your component
- Only call the returned function inside `useEffect`, `useLayoutEffect`, or `useInsertionEffect`
- Do not pass effect events to other components or hooks

## `useId` (Hydration-Safe IDs)

Generates unique IDs that are consistent between server and client rendering:

```tsx
import { useId } from 'react';

function PasswordField() {
  const passwordId = useId();
  const hintId = useId();
  return (
    <div>
      <label htmlFor={passwordId}>Password</label>
      <input id={passwordId} type="password" aria-describedby={hintId} />
      <p id={hintId}>Must be at least 8 characters</p>
    </div>
  );
}
```

Never use `Math.random()`, incrementing counters, or `Date.now()` for IDs in server-rendered components.

## React Query (Client-Side Server State)

```tsx
const { data, isLoading, error } = useQuery({
  queryKey: ['users'],
  queryFn: fetchUsers,
  staleTime: 5 * 60 * 1000,
});
```

## Narrow Effect Dependencies

Specify primitive dependencies instead of objects to minimize effect re-runs:

```tsx
// Better
useEffect(() => {
  track(user.id);
}, [user.id]);

// Worse
useEffect(() => {
  track(user.id);
}, [user]);
```
