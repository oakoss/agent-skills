---
title: Forms and Validation
description: Form handling with React Hook Form and Zod validation, Server Actions with useActionState, optimistic form updates, and multi-step form patterns
tags:
  [
    forms,
    react-hook-form,
    zod,
    validation,
    server-actions,
    useActionState,
    useOptimistic,
  ]
---

# Forms and Validation

## Choosing an Approach

| Pattern                          | When to Use                                     |
| -------------------------------- | ----------------------------------------------- |
| Server Action + `useActionState` | Simple forms with server-side validation        |
| React Hook Form + Zod            | Complex client-side forms with instant feedback |
| Server Action + React Hook Form  | Client validation first, then server mutation   |

## React Hook Form with Zod

Standard approach for complex forms with immediate client-side validation.

```tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  role: z.enum(['admin', 'editor', 'viewer']),
  bio: z.string().max(500, 'Bio must be under 500 characters').optional(),
});

type CreateUserForm = z.infer<typeof createUserSchema>;

export function CreateUserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<CreateUserForm>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      role: 'viewer',
    },
  });

  const onSubmit = async (data: CreateUserForm) => {
    const res = await fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (res.ok) reset();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="text-sm font-medium">Name</label>
        <input
          {...register('name')}
          className="border rounded px-3 py-2 w-full"
        />
        {errors.name ? (
          <p className="text-sm text-destructive">{errors.name.message}</p>
        ) : null}
      </div>

      <div>
        <label className="text-sm font-medium">Email</label>
        <input
          {...register('email')}
          type="email"
          className="border rounded px-3 py-2 w-full"
        />
        {errors.email ? (
          <p className="text-sm text-destructive">{errors.email.message}</p>
        ) : null}
      </div>

      <div>
        <label className="text-sm font-medium">Role</label>
        <select
          {...register('role')}
          className="border rounded px-3 py-2 w-full"
        >
          <option value="viewer">Viewer</option>
          <option value="editor">Editor</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      <div>
        <label className="text-sm font-medium">Bio</label>
        <textarea
          {...register('bio')}
          className="border rounded px-3 py-2 w-full"
        />
        {errors.bio ? (
          <p className="text-sm text-destructive">{errors.bio.message}</p>
        ) : null}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="bg-primary text-primary-foreground px-4 py-2 rounded"
      >
        {isSubmitting ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
}
```

## Server Actions with useActionState

For forms that submit directly to the server with built-in pending state management.

### Define the Action

```tsx
// app/contacts/actions.ts
'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const contactSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
});

export type ContactState = {
  errors?: Record<string, string[]>;
  message?: string;
} | null;

export async function submitContact(
  _prevState: ContactState,
  formData: FormData,
): Promise<ContactState> {
  const result = contactSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    message: formData.get('message'),
  });

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }

  await db.insert(contacts).values(result.data);
  revalidatePath('/contacts');

  return { message: 'Message sent successfully!' };
}
```

### Use in a Client Component

```tsx
// components/features/contact-form.tsx
'use client';

import { useActionState } from 'react';
import { submitContact } from '@/app/contacts/actions';

export function ContactForm() {
  const [state, formAction, isPending] = useActionState(submitContact, null);

  return (
    <form action={formAction} className="space-y-4">
      <div>
        <label className="text-sm font-medium">Name</label>
        <input
          name="name"
          required
          className="border rounded px-3 py-2 w-full"
        />
        {state?.errors?.name ? (
          <p className="text-sm text-destructive">{state.errors.name[0]}</p>
        ) : null}
      </div>

      <div>
        <label className="text-sm font-medium">Email</label>
        <input
          name="email"
          type="email"
          required
          className="border rounded px-3 py-2 w-full"
        />
        {state?.errors?.email ? (
          <p className="text-sm text-destructive">{state.errors.email[0]}</p>
        ) : null}
      </div>

      <div>
        <label className="text-sm font-medium">Message</label>
        <textarea
          name="message"
          required
          className="border rounded px-3 py-2 w-full"
        />
        {state?.errors?.message ? (
          <p className="text-sm text-destructive">{state.errors.message[0]}</p>
        ) : null}
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="bg-primary text-primary-foreground px-4 py-2 rounded"
      >
        {isPending ? 'Sending...' : 'Send Message'}
      </button>

      {state?.message ? (
        <p className="text-sm text-green-600">{state.message}</p>
      ) : null}
    </form>
  );
}
```

## Optimistic Form Updates

Use `useOptimistic` to show immediate feedback while the server processes the mutation.

```tsx
'use client';

import { useOptimistic } from 'react';
import { type Todo } from '@/lib/types';
import { toggleTodo } from '@/app/todos/actions';

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, setOptimisticTodo] = useOptimistic(
    todos,
    (state, updatedId: string) =>
      state.map((todo) =>
        todo.id === updatedId ? { ...todo, completed: !todo.completed } : todo,
      ),
  );

  return (
    <ul className="space-y-2">
      {optimisticTodos.map((todo) => (
        <li key={todo.id} className="flex items-center gap-2">
          <form
            action={async () => {
              setOptimisticTodo(todo.id);
              await toggleTodo(todo.id);
            }}
          >
            <button type="submit">{todo.completed ? '[x]' : '[ ]'}</button>
          </form>
          <span className={todo.completed ? 'line-through opacity-50' : ''}>
            {todo.title}
          </span>
        </li>
      ))}
    </ul>
  );
}
```

## Shared Zod Schemas

Define schemas once and reuse for both client validation and Server Actions.

```tsx
// lib/schemas.ts
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export const signupSchema = loginSchema
  .extend({
    name: z.string().min(2, 'Name required'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export type LoginInput = z.infer<typeof loginSchema>;
export type SignupInput = z.infer<typeof signupSchema>;
```
