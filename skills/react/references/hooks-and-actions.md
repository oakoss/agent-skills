---
title: Hooks and Server Actions
description: React 19 use() API, useActionState, useOptimistic, useTransition, and useEffectEvent patterns
tags:
  [
    hooks,
    use,
    useActionState,
    useOptimistic,
    useTransition,
    server-actions,
    forms,
  ]
---

# Hooks and Server Actions

## The `use()` API (React 19)

Replaces the `useEffect` + `useState` fetch pattern. Unwraps promises or context values within the render body.

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

## `useOptimistic` (Instant UI Feedback)

Show temporary state while an async action is in flight:

```tsx
import { useOptimistic } from 'react';

function ChatList({ messages }) {
  const [optimisticMessages, addOptimisticMessage] = useOptimistic(
    messages,
    (state, newMessage) => [...state, { text: newMessage, sending: true }],
  );

  async function formAction(formData) {
    const text = formData.get('message');
    addOptimisticMessage(text);
    await sendMessage(text);
  }

  return (
    <div>
      {optimisticMessages.map((m) => (
        <div key={m.id}>{m.text}</div>
      ))}
      <form action={formAction}>
        <input name="message" />
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

## `useEffectEvent` (React 19.2+)

For logic that depends on reactive values but shouldn't trigger the effect:

```tsx
function Chat({ roomId, theme }) {
  const onConnected = useEffectEvent(() => {
    logAnalytics('Connected', { theme }); // theme captured but doesn't re-run effect
  });

  useEffect(() => {
    const socket = connect(roomId);
    socket.on('connect', onConnected);
    return () => socket.disconnect();
  }, [roomId]); // theme is NOT a dependency
}
```

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
