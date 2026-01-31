---
title: Field Validation
description: Sync and async validation, debouncing, and linked fields
tags: [validation, sync, async, debounce, linked-fields]
---

# Field Validation

## Validation Timing

```tsx
<form.Field
  name="email"
  validators={{
    onChange: ({ value }) =>
      !value.includes('@') ? 'Invalid email' : undefined,
    onBlur: ({ value }) =>
      value.length === 0 ? 'Email is required' : undefined,
    onSubmit: ({ value }) =>
      value.endsWith('@example.com') ? 'Example emails not allowed' : undefined,
  }}
  children={(field) => (
    <input
      value={field.state.value}
      onChange={(e) => field.handleChange(e.target.value)}
      onBlur={field.handleBlur}
    />
  )}
/>
```

| Timing     | When It Runs                       | Use Case                       |
| ---------- | ---------------------------------- | ------------------------------ |
| `onChange` | Every time the field value changes | Real-time feedback             |
| `onBlur`   | When the user leaves the field     | Deferred validation            |
| `onSubmit` | When the form is submitted         | Final validation before submit |

## Sync Validation

Validators receive a context object:

```tsx
type ValidatorContext = {
  value: T;
  fieldApi: FieldApi<TFormData, TName>;
};

<form.Field
  name="username"
  validators={{
    onChange: ({ value }) => {
      if (!value) return 'Username is required';
      if (value.length < 3) return 'Username must be at least 3 characters';
      if (!/^[a-z0-9_]+$/.test(value))
        return 'Username can only contain lowercase letters, numbers, and underscores';
      return undefined;
    },
  }}
/>;
```

## Async Validation

Debounce async validators to avoid excessive server requests:

```tsx
<form.Field
  name="email"
  validators={{
    onChange: ({ value }) =>
      !value.includes('@') ? 'Invalid email format' : undefined,
    onChangeAsyncDebounceMs: 500,
    onChangeAsync: async ({ value }) => {
      const response = await fetch(`/api/check-email?email=${value}`);
      const data = await response.json();
      return data.available ? undefined : 'Email already taken';
    },
  }}
  children={(field) => (
    <div>
      <input
        value={field.state.value}
        onChange={(e) => field.handleChange(e.target.value)}
      />
      {field.state.meta.isValidating && <span>Checking...</span>}
      {field.state.meta.isTouched && field.state.meta.errors.length > 0 && (
        <em>{field.state.meta.errors.join(', ')}</em>
      )}
    </div>
  )}
/>
```

## Debounce Configuration

Set a default debounce for all async validators on a field:

```tsx
<form.Field
  name="username"
  asyncDebounceMs={500}
  validators={{
    onChange: ({ value }) => (value.length < 3 ? 'Too short' : undefined),
    onChangeAsync: async ({ value }) => {
      const available = await checkUsername(value);
      return available ? undefined : 'Username taken';
    },
    onBlurAsync: async ({ value }) => {
      return validateWithServer(value);
    },
  }}
/>
```

Override debounce per validator:

```tsx
<form.Field
  name="username"
  asyncDebounceMs={500}
  validators={{
    onChangeAsyncDebounceMs: 1000,
    onChangeAsync: async ({ value }) => {
      return checkAvailability(value);
    },
  }}
/>
```

## Linked Fields

Re-validate a field when another field changes:

```tsx
<form.Field
  name="password"
  children={(field) => (
    <input
      type="password"
      value={field.state.value}
      onChange={(e) => field.handleChange(e.target.value)}
    />
  )}
/>

<form.Field
  name="confirmPassword"
  validators={{
    onChangeListenTo: ['password'],
    onChange: ({ value, fieldApi }) => {
      if (value !== fieldApi.form.getFieldValue('password')) {
        return 'Passwords do not match';
      }
      return undefined;
    },
  }}
  children={(field) => (
    <div>
      <input
        type="password"
        value={field.state.value}
        onChange={(e) => field.handleChange(e.target.value)}
      />
      {field.state.meta.isTouched && field.state.meta.errors.length > 0 && (
        <em>{field.state.meta.errors.join(', ')}</em>
      )}
    </div>
  )}
/>
```

Multiple dependencies:

```tsx
<form.Field
  name="endDate"
  validators={{
    onChangeListenTo: ['startDate', 'duration'],
    onChange: ({ value, fieldApi }) => {
      const startDate = fieldApi.form.getFieldValue('startDate');
      const duration = fieldApi.form.getFieldValue('duration');

      if (new Date(value) <= new Date(startDate)) {
        return 'End date must be after start date';
      }

      const diffDays = Math.floor(
        (new Date(value).getTime() - new Date(startDate).getTime()) /
          (1000 * 60 * 60 * 24),
      );

      if (diffDays > duration) {
        return `Duration cannot exceed ${duration} days`;
      }

      return undefined;
    },
  }}
/>
```

## Conditional Validation

Validate based on other field values:

```tsx
<form.Field
  name="companyName"
  validators={{
    onChangeListenTo: ['accountType'],
    onChange: ({ value, fieldApi }) => {
      const accountType = fieldApi.form.getFieldValue('accountType');

      if (accountType === 'business' && !value) {
        return 'Company name is required for business accounts';
      }

      return undefined;
    },
  }}
/>
```

## Server-Side Validation

Async validation with server:

```tsx
const checkUsername = async (username: string) => {
  const response = await fetch('/api/check-username', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  });
  return response.json();
};

<form.Field
  name="username"
  validators={{
    onChange: ({ value }) => {
      if (value.length < 3) return 'Too short';
      if (!/^[a-z0-9_]+$/.test(value)) return 'Invalid characters';
      return undefined;
    },
    onChangeAsyncDebounceMs: 500,
    onChangeAsync: async ({ value }) => {
      const result = await checkUsername(value);
      return result.available ? undefined : 'Username already taken';
    },
  }}
/>;
```

Form-level async validation:

```tsx
const form = useForm({
  defaultValues: { email: '', username: '' },
  validators: {
    onSubmitAsync: async ({ value }) => {
      const result = await fetch('/api/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(value),
      }).then((r) => r.json());

      if (!result.valid) {
        return {
          form: 'Invalid data',
          fields: {
            email: result.errors.email,
            username: result.errors.username,
          },
        };
      }

      return null;
    },
  },
});
```

## Error Display Patterns

Show errors after touched:

```tsx
const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;

{
  isInvalid && (
    <span className="text-red-600">{field.state.meta.errors.join(', ')}</span>
  );
}
```

Show errors immediately:

```tsx
{
  field.state.meta.errors.length > 0 && (
    <span className="text-red-600">{field.state.meta.errors.join(', ')}</span>
  );
}
```

Show first error only:

```tsx
{
  field.state.meta.isTouched && field.state.meta.errors[0] && (
    <span className="text-red-600">{field.state.meta.errors[0]}</span>
  );
}
```

## Validation Notes

- Always validate on both client and server
- Return `undefined` for valid state, error string for invalid
- Async validators return `Promise<string | undefined>`
- Use debouncing for expensive async validation
- `onChangeListenTo` triggers re-validation when dependencies change
- Form-level validators can return `{ form: string, fields: Record<string, string> }`
