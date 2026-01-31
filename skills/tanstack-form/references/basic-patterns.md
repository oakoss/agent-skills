---
title: Basic Patterns
description: Core form setup, field rendering, form submission, and state management
tags: [useForm, field, submission, state, handleSubmit]
---

# Basic Patterns

## Installation

```bash
pnpm add @tanstack/react-form
```

## Basic Form

```tsx
import { useForm } from '@tanstack/react-form';
import type { AnyFieldApi } from '@tanstack/react-form';

function FieldInfo({ field }: { field: AnyFieldApi }) {
  return (
    <>
      {field.state.meta.isTouched && !field.state.meta.isValid ? (
        <em>{field.state.meta.errors.join(', ')}</em>
      ) : null}
      {field.state.meta.isValidating ? 'Validating...' : null}
    </>
  );
}

function App() {
  const form = useForm({
    defaultValues: {
      firstName: '',
      lastName: '',
    },
    onSubmit: async ({ value }) => {
      console.log(value);
    },
  });

  return (
    <div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          e.stopPropagation();
          form.handleSubmit();
        }}
      >
        <div>
          <form.Field
            name="firstName"
            children={(field) => (
              <>
                <label htmlFor={field.name}>First Name:</label>
                <input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => field.handleChange(e.target.value)}
                />
                <FieldInfo field={field} />
              </>
            )}
          />
        </div>
        <div>
          <form.Field
            name="lastName"
            children={(field) => (
              <>
                <label htmlFor={field.name}>Last Name:</label>
                <input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => field.handleChange(e.target.value)}
                />
                <FieldInfo field={field} />
              </>
            )}
          />
        </div>
        <form.Subscribe
          selector={(state) => [state.canSubmit, state.isSubmitting]}
          children={([canSubmit, isSubmitting]) => (
            <button type="submit" disabled={!canSubmit}>
              {isSubmitting ? '...' : 'Submit'}
            </button>
          )}
        />
      </form>
    </div>
  );
}
```

## Form Field Render Props

The `field` object passed to the render function provides:

| Property                  | Type                      | Description                      |
| ------------------------- | ------------------------- | -------------------------------- |
| `state.value`             | `T`                       | Current field value              |
| `state.meta.errors`       | `string[]`                | Current validation errors        |
| `state.meta.isTouched`    | `boolean`                 | User has interacted with field   |
| `state.meta.isValid`      | `boolean`                 | Field passes all validators      |
| `state.meta.isValidating` | `boolean`                 | Async validation in progress     |
| `handleChange`            | `(value: T) => void`      | Update field value               |
| `handleBlur`              | `() => void`              | Mark field as touched            |
| `name`                    | `string`                  | Field name from `name` prop      |
| `pushValue`               | `(value: T) => void`      | Add to array (mode="array" only) |
| `removeValue`             | `(index: number) => void` | Remove from array (mode="array") |

## Form State

Access form-level state:

```tsx
const form = useForm({
  defaultValues: { email: '' },
  onSubmit: async ({ value }) => {
    await submitToServer(value);
  },
});

form.state.values;
form.state.errors;
form.state.isSubmitting;
form.state.isValid;
form.state.isDirty;
form.state.canSubmit;

form.reset();
form.handleSubmit();
form.getFieldValue('email');
form.setFieldValue('email', 'new@example.com');
```

## Subscribe to Form State

Use `form.Subscribe` to avoid re-rendering the entire form:

```tsx
<form.Subscribe
  selector={(state) => [state.canSubmit, state.isSubmitting]}
  children={([canSubmit, isSubmitting]) => (
    <button type="submit" disabled={!canSubmit}>
      {isSubmitting ? 'Submitting...' : 'Submit'}
    </button>
  )}
/>
```

## Form Submission

The `onSubmit` callback receives:

```tsx
type SubmitEvent = {
  value: TFormData;
  formApi: FormApi<TFormData>;
};

const form = useForm({
  defaultValues: { name: '', email: '' },
  onSubmit: async ({ value, formApi }) => {
    try {
      await api.createUser(value);
      formApi.reset();
    } catch (error) {
      formApi.setFieldMeta('email', (prev) => ({
        ...prev,
        errors: ['Email already exists'],
      }));
    }
  },
});
```

## Form-Level Validation

Return field errors from form-level validators:

```tsx
const form = useForm({
  defaultValues: {
    age: 0,
    email: '',
  },
  validators: {
    onSubmit: ({ value }) => {
      const errors: Record<string, string> = {};

      if (value.age < 13) {
        errors.age = 'Must be 13 or older';
      }

      if (!value.email.includes('@')) {
        errors.email = 'Invalid email format';
      }

      return Object.keys(errors).length > 0 ? { fields: errors } : undefined;
    },
  },
});
```

## Async Form Validation

Validate against server:

```tsx
const form = useForm({
  defaultValues: { email: '', username: '' },
  validators: {
    onSubmitAsync: async ({ value }) => {
      const result = await api.validateUser(value);

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

<form.Subscribe
  selector={(state) => [state.errorMap]}
  children={([errorMap]) =>
    errorMap.onSubmit ? (
      <div>
        <em>There was an error on the form: {errorMap.onSubmit}</em>
      </div>
    ) : null
  }
/>;
```

## Nested Object Fields

Access nested fields with dot notation:

```tsx
type FormData = {
  user: {
    name: string;
    email: string;
  };
};

const form = useForm<FormData>({
  defaultValues: {
    user: {
      name: '',
      email: '',
    },
  },
});

<form.Field
  name="user.name"
  children={(field) => (
    <input
      value={field.state.value}
      onChange={(e) => field.handleChange(e.target.value)}
    />
  )}
/>

<form.Field
  name="user.email"
  children={(field) => (
    <input
      value={field.state.value}
      onChange={(e) => field.handleChange(e.target.value)}
    />
  )}
/>
```

## Controlled vs Uncontrolled

TanStack Form uses controlled inputs by default. For uncontrolled inputs with refs:

```tsx
import { useRef } from 'react';

function UncontrolledForm() {
  const form = useForm({
    defaultValues: { email: '' },
    onSubmit: async ({ value }) => {
      console.log(value);
    },
  });

  return (
    <form.Field
      name="email"
      children={(field) => {
        const inputRef = useRef<HTMLInputElement>(null);

        return (
          <input
            ref={inputRef}
            defaultValue={field.state.value}
            onBlur={() => {
              field.handleChange(inputRef.current?.value ?? '');
              field.handleBlur();
            }}
          />
        );
      }}
    />
  );
}
```

Controlled inputs are recommended for better validation timing and state management.

## Reset Form

Reset to default values:

```tsx
const form = useForm({
  defaultValues: { email: '', name: '' },
  onSubmit: async ({ value, formApi }) => {
    await api.submit(value);
    formApi.reset();
  },
});

<button type="button" onClick={() => form.reset()}>
  Reset
</button>;
```

## Set Field Value Programmatically

```tsx
const form = useForm({
  defaultValues: { country: '', province: '' },
});

<form.Field
  name="country"
  children={(field) => (
    <select
      value={field.state.value}
      onChange={(e) => {
        field.handleChange(e.target.value);
        form.setFieldValue('province', '');
      }}
    >
      <option value="">Select country</option>
      <option value="us">United States</option>
      <option value="ca">Canada</option>
    </select>
  )}
/>;
```
