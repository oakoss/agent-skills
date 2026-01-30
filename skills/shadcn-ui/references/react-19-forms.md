---
title: React 19 Form Patterns
description: Server Actions, useFormStatus, useFormState, useOptimistic, and Zod validation patterns with shadcn/ui form components
tags: [react-19, forms, server-actions, zod, validation]
---

# React 19 Form Patterns

React 19 simplifies form management through native hooks and Server Actions integration. shadcn/ui Form components pair with Zod schemas for type-safe validation.

## Native Status Handling

Use `useFormStatus` inside shadcn/ui buttons to provide immediate feedback during form submission:

```tsx
import { useFormStatus } from 'react-dom';
import { Button } from '@/components/ui/button';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <Button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Save'}
    </Button>
  );
}
```

`useFormStatus` must be called from a component that is a child of a `<form>`. It does not work if called in the same component that renders the form element.

## Server Action State

Combine `useActionState` (renamed from `useFormState` in React 19) with Zod validation for backend-to-frontend error communication:

```tsx
'use server';

import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
});

type FormState = {
  errors: Record<string, string[]>;
  message?: string;
};

export async function createUser(
  _prevState: FormState,
  formData: FormData,
): Promise<FormState> {
  const result = schema.safeParse({
    email: formData.get('email'),
    name: formData.get('name'),
  });

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }

  return { errors: {}, message: 'User created' };
}
```

```tsx
'use client';

import { useActionState } from 'react';
import { createUser } from './actions';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function CreateUserForm() {
  const [state, formAction, isPending] = useActionState(createUser, {
    errors: {},
  });

  return (
    <form action={formAction}>
      <div>
        <Label htmlFor="name">Name</Label>
        <Input id="name" name="name" />
        {state.errors.name ? (
          <p className="text-sm text-destructive">{state.errors.name[0]}</p>
        ) : null}
      </div>
      <div>
        <Label htmlFor="email">Email</Label>
        <Input id="email" name="email" type="email" />
        {state.errors.email ? (
          <p className="text-sm text-destructive">{state.errors.email[0]}</p>
        ) : null}
      </div>
      <Button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create User'}
      </Button>
      {state.message ? (
        <p className="text-sm text-muted-foreground">{state.message}</p>
      ) : null}
    </form>
  );
}
```

## Optimistic Updates

Use `useOptimistic` for instant UI feedback during long-running Server Actions:

```tsx
'use client';

import { useOptimistic } from 'react';
import { type Todo } from '@/lib/types';
import { toggleTodo } from './actions';

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, setOptimisticTodo] = useOptimistic(
    todos,
    (state: Todo[], updatedId: string) =>
      state.map((todo) =>
        todo.id === updatedId ? { ...todo, completed: !todo.completed } : todo,
      ),
  );

  async function handleToggle(id: string) {
    setOptimisticTodo(id);
    await toggleTodo(id);
  }

  return (
    <ul>
      {optimisticTodos.map((todo) => (
        <li key={todo.id}>
          <button type="button" onClick={() => handleToggle(todo.id)}>
            {todo.completed ? 'Done' : 'Pending'}: {todo.title}
          </button>
        </li>
      ))}
    </ul>
  );
}
```

## shadcn/ui Form with React Hook Form and Zod

The shadcn/ui Form component wraps React Hook Form with accessible field components:

```tsx
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';

const formSchema = z.object({
  username: z.string().min(2, 'Username must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
});

type FormValues = z.infer<typeof formSchema>;

export function ProfileForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: '', email: '' },
  });

  function onSubmit(values: FormValues) {
    console.log(values);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="username" {...field} />
              </FormControl>
              <FormDescription>Your public display name.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="email@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Save</Button>
      </form>
    </Form>
  );
}
```

## Hook Selection Guide

| Pattern                        | Hook             | Notes                                |
| ------------------------------ | ---------------- | ------------------------------------ |
| Submit button loading state    | `useFormStatus`  | Must be child of `<form>`            |
| Server Action with error state | `useActionState` | Returns `[state, action, isPending]` |
| Instant UI feedback            | `useOptimistic`  | Reverts on Server Action failure     |
| Client-side validation         | `useForm` + Zod  | React Hook Form with zodResolver     |
