---
title: Form+Query Integration
description: TanStack Form setup with Zod validation, field-level and async validation, field arrays, custom components, and Query cache integration
tags:
  [
    form,
    mutation,
    invalidation,
    optimistic,
    useMutation,
    useForm,
    zod,
    validation,
    field-arrays,
  ]
---

# Form+Query Integration

## Basic Form Setup with Zod

```tsx
import { useForm } from '@tanstack/react-form';
import { zodValidator } from '@tanstack/zod-form-adapter';
import { z } from 'zod';

const userSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  age: z.number().min(18, 'Must be at least 18'),
});

type UserFormData = z.infer<typeof userSchema>;

function UserForm() {
  const form = useForm({
    defaultValues: { name: '', email: '', age: 0 } satisfies UserFormData,
    onSubmit: async ({ value }) => {
      await api.createUser(value);
    },
    validatorAdapter: zodValidator(),
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        form.handleSubmit();
      }}
    >
      <form.Field name="name" validators={{ onChange: z.string().min(2) }}>
        {(field) => (
          <div>
            <label htmlFor={field.name}>Name</label>
            <input
              id={field.name}
              value={field.state.value}
              onBlur={field.handleBlur}
              onChange={(e) => field.handleChange(e.target.value)}
            />
            {field.state.meta.errors.length > 0 && (
              <span className="error">{field.state.meta.errors[0]}</span>
            )}
          </div>
        )}
      </form.Field>

      <form.Subscribe
        selector={(state) => [state.canSubmit, state.isSubmitting]}
      >
        {([canSubmit, isSubmitting]) => (
          <button type="submit" disabled={!canSubmit || isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
        )}
      </form.Subscribe>
    </form>
  );
}
```

## Form-Level Validation (Cross-Field)

```tsx
const form = useForm({
  defaultValues: { password: '', confirmPassword: '' },
  validatorAdapter: zodValidator(),
  validators: {
    onChange: z
      .object({
        password: z.string(),
        confirmPassword: z.string(),
      })
      .refine((data) => data.password === data.confirmPassword, {
        message: "Passwords don't match",
        path: ['confirmPassword'],
      }),
  },
  onSubmit: async ({ value }) => {
    /* submit */
  },
});
```

## Async Validation

```tsx
<form.Field
  name="username"
  validators={{
    onChange: z.string().min(3),
    onBlurAsync: async ({ value }) => {
      const isAvailable = await checkUsernameAvailable(value);
      if (!isAvailable) return 'Username is already taken';
      return undefined;
    },
    onBlurAsyncDebounceMs: 500,
  }}
>
  {(field) => (
    <div>
      <input
        value={field.state.value}
        onChange={(e) => field.handleChange(e.target.value)}
        onBlur={field.handleBlur}
      />
      {field.state.meta.isValidating && <span>Checking...</span>}
    </div>
  )}
</form.Field>
```

## Form Submission with Error Handling

```tsx
const form = useForm({
  defaultValues: { name: '', email: '' },
  onSubmit: async ({ value, formApi }) => {
    try {
      await api.createUser(value);
      formApi.reset();
    } catch (error) {
      formApi.setErrorMap({ onSubmit: error.message });
    }
  },
});
```

Display submission errors and reset:

```tsx
<form.Subscribe selector={(state) => state.errorMap.onSubmit}>
  {(error) => error && <div className="error">{error}</div>}
</form.Subscribe>

<form.Subscribe
  selector={(state) => ({
    canSubmit: state.canSubmit,
    isSubmitting: state.isSubmitting,
    isDirty: state.isDirty,
  })}
>
  {({ canSubmit, isSubmitting, isDirty }) => (
    <div>
      <button type="submit" disabled={!canSubmit || isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save'}
      </button>
      <button type="button" onClick={() => form.reset()} disabled={!isDirty}>
        Reset
      </button>
    </div>
  )}
</form.Subscribe>
```

## Field Arrays

```tsx
<form.Field name="users" mode="array">
  {(field) => (
    <div>
      {field.state.value.map((_, index) => (
        <div key={index}>
          <form.Field name={`users[${index}].name`}>
            {(subField) => (
              <input
                placeholder="Name"
                value={subField.state.value}
                onChange={(e) => subField.handleChange(e.target.value)}
              />
            )}
          </form.Field>
          <button
            type="button"
            onClick={() => field.removeValue(index)}
            disabled={field.state.value.length <= 1}
          >
            Remove
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() => field.pushValue({ name: '', email: '' })}
      >
        Add User
      </button>
    </div>
  )}
</form.Field>
```

## Custom Field Components

```tsx
import { useFieldContext } from '@tanstack/react-form';

interface TextFieldProps {
  label: string;
  type?: 'text' | 'email' | 'password';
  placeholder?: string;
}

export function TextField({
  label,
  type = 'text',
  placeholder,
}: TextFieldProps) {
  const field = useFieldContext();
  return (
    <div className="form-field">
      <label htmlFor={field.name}>{label}</label>
      <input
        id={field.name}
        type={type}
        placeholder={placeholder}
        value={field.state.value}
        onChange={(e) => field.handleChange(e.target.value)}
        onBlur={field.handleBlur}
        className={`form-input ${field.state.meta.errors.length > 0 ? 'error' : ''}`}
      />
      {field.state.meta.isTouched && field.state.meta.errors.length > 0 && (
        <span className="form-error">{field.state.meta.errors[0]}</span>
      )}
    </div>
  );
}
```

## Query Cache Invalidation

Invalidate query cache after form submission:

```tsx
const queryClient = useQueryClient();

const form = useForm({
  defaultValues: { title: '', body: '' },
  onSubmit: async ({ value }) => {
    await createPost(value);
    await queryClient.invalidateQueries({ queryKey: ['posts'] });
    navigate({ to: '/posts' });
  },
});
```

## Optimistic Form Submissions

Pair `useForm` with `useMutation` for optimistic updates:

```tsx
const updateMutation = useMutation({
  mutationFn: (data: UpdateUserDto) => api.updateUser(userId, data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
  },
});

const form = useForm({
  defaultValues: { name: user.name, email: user.email, bio: user.bio ?? '' },
  onSubmit: async ({ value }) => {
    await updateMutation.mutateAsync(value);
  },
});
```

Display mutation state in the submit button:

```tsx
<form.Subscribe selector={(state) => state.isSubmitting}>
  {(isSubmitting) => (
    <button type="submit" disabled={isSubmitting || updateMutation.isPending}>
      {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
    </button>
  )}
</form.Subscribe>;
{
  updateMutation.isError && (
    <div className="error">{updateMutation.error.message}</div>
  );
}
```

## Anti-Patterns

- **Loading waterfalls**: Use `ensureQueryData` in route loaders, not `useQuery` in components
- **Global QueryClient singleton**: Create QueryClient per request inside `getRouter()` for SSR safety
- **Manual SSR dehydration**: Use `setupRouterSsrQueryIntegration` instead of manual `dehydrate`/`hydrate`
- **Premature adoption**: Build vanilla first, adopt TanStack selectively where clear benefit exists
