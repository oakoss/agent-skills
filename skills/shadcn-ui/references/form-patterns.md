---
title: Form Patterns
description: Building forms with shadcn/ui Field component, React Hook Form, TanStack Form, Zod validation, Server Actions, and React 19 hooks
tags:
  [
    forms,
    field,
    react-hook-form,
    tanstack-form,
    zod,
    server-actions,
    validation,
  ]
---

# Form Patterns

shadcn/ui provides the `<Field />` component as the current approach for building forms. The legacy `<Form />` component still works but is no longer actively developed.

## Field Component with React Hook Form

The recommended pattern using `<Field />`, `<FieldError />`, and React Hook Form with Zod:

```tsx
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Field, FieldError } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const formSchema = z.object({
  username: z.string().min(2, 'Username must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
});

type FormValues = z.infer<typeof formSchema>;

export function ProfileForm() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: '', email: '' },
  });

  function onSubmit(values: FormValues) {
    console.log(values);
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Field>
        <Label htmlFor="username">Username</Label>
        <Controller
          control={control}
          name="username"
          render={({ field }) => (
            <Input id="username" placeholder="username" {...field} />
          )}
        />
        <FieldError
          errors={
            errors.username?.message ? [errors.username.message] : undefined
          }
        />
      </Field>
      <Field>
        <Label htmlFor="email">Email</Label>
        <Controller
          control={control}
          name="email"
          render={({ field }) => (
            <Input id="email" placeholder="email@example.com" {...field} />
          )}
        />
        <FieldError
          errors={errors.email?.message ? [errors.email.message] : undefined}
        />
      </Field>
      <Button type="submit">Save</Button>
    </form>
  );
}
```

## FieldError with Standard Schema

`FieldError` accepts issues from any validator implementing Standard Schema, including Zod, Valibot, and ArkType:

```tsx
import { FieldError } from '@/components/ui/field';

<FieldError
  errors={['Username is required', 'Must be at least 2 characters']}
/>;
```

## Server Action with useActionState

Combine `useActionState` with Zod validation for server-side form handling:

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
import { Field, FieldError } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function CreateUserForm() {
  const [state, formAction, isPending] = useActionState(createUser, {
    errors: {},
  });

  return (
    <form action={formAction} className="space-y-4">
      <Field>
        <Label htmlFor="name">Name</Label>
        <Input id="name" name="name" />
        <FieldError errors={state.errors.name} />
      </Field>
      <Field>
        <Label htmlFor="email">Email</Label>
        <Input id="email" name="email" type="email" />
        <FieldError errors={state.errors.email} />
      </Field>
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

## Submit Button with useFormStatus

Use `useFormStatus` inside a child component of `<form>` for pending state:

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

`useFormStatus` must be called from a component that is a **child** of a `<form>`. It does not work if called in the same component that renders the form element.

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

## Legacy Form Component

The legacy `<Form />` wrapper around React Hook Form still works but is no longer actively developed. For existing projects using it:

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
});

type FormValues = z.infer<typeof formSchema>;

export function LegacyProfileForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: '' },
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
        <Button type="submit">Save</Button>
      </form>
    </Form>
  );
}
```

## Hook Selection Guide

| Pattern                        | Hook                 | Notes                                |
| ------------------------------ | -------------------- | ------------------------------------ |
| Submit button loading state    | `useFormStatus`      | Must be child of `<form>`            |
| Server Action with error state | `useActionState`     | Returns `[state, action, isPending]` |
| Instant UI feedback            | `useOptimistic`      | Reverts on Server Action failure     |
| Client-side validation         | `useForm` + Zod      | React Hook Form with zodResolver     |
| Server-side validation         | Zod in Server Action | Return flattened field errors        |

## Form Library Choice

shadcn/ui supports multiple form libraries:

| Library         | Best For                                                        |
| --------------- | --------------------------------------------------------------- |
| React Hook Form | Client-heavy forms, complex validation, existing RHF projects   |
| TanStack Form   | Framework-agnostic projects, type-safe form state               |
| Next.js Form    | Progressive enhancement, Server Actions with Next.js `<Form />` |
| Native `<form>` | Simple forms with `useActionState` and server-side validation   |
