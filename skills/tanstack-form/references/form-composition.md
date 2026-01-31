---
title: Form Composition
description: Reusable field components with createFormHook and form contexts
tags: [composition, createFormHook, context, reusable, fieldComponents]
---

# Form Composition

## Why Form Composition

The basic `useForm` pattern works for one-off forms, but repeating field components across forms leads to duplication. Form composition enables:

- Reusable field components with consistent styling
- Type-safe field access via context
- Centralized form component library
- Reduced boilerplate in form definitions

## Setup Form Contexts

Create shared contexts for field and form access:

```tsx
// src/hooks/form-context.ts
import { createFormHookContexts } from '@tanstack/react-form';

export const { fieldContext, formContext, useFieldContext, useFormContext } =
  createFormHookContexts();
```

## Create Reusable Field Components

Field components use `useFieldContext` to access field state:

```tsx
// src/components/form/text-field.tsx
import { useFieldContext } from '@/hooks/form-context';
import { useStore } from '@tanstack/react-form';

export function FormTextField({
  label,
  placeholder,
  type = 'text',
}: {
  label: string;
  placeholder?: string;
  type?: 'text' | 'email' | 'password';
}) {
  const field = useFieldContext<string>();
  const errors = useStore(field.store, (s) => s.meta.errors);
  const isInvalid = field.state.meta.isTouched && errors.length > 0;

  return (
    <div>
      <label htmlFor={field.name}>{label}</label>
      <input
        id={field.name}
        type={type}
        value={field.state.value}
        placeholder={placeholder}
        onBlur={field.handleBlur}
        onChange={(e) => field.handleChange(e.target.value)}
        aria-invalid={isInvalid}
      />
      {isInvalid && <span className="error">{errors.join(', ')}</span>}
    </div>
  );
}
```

## Create Select Field Component

```tsx
// src/components/form/select-field.tsx
import { useFieldContext } from '@/hooks/form-context';

export function FormSelectField({
  label,
  options,
  placeholder,
}: {
  label: string;
  options: Array<{ label: string; value: string }>;
  placeholder?: string;
}) {
  const field = useFieldContext<string>();

  return (
    <div>
      <label htmlFor={field.name}>{label}</label>
      <select
        id={field.name}
        value={field.state.value}
        onChange={(e) => field.handleChange(e.target.value)}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
```

## Create Switch Field Component

```tsx
// src/components/form/switch-field.tsx
import { useFieldContext } from '@/hooks/form-context';

export function FormSwitchField({ label }: { label: string }) {
  const field = useFieldContext<boolean>();

  return (
    <label>
      <input
        type="checkbox"
        checked={field.state.value}
        onChange={(e) => field.handleChange(e.target.checked)}
      />
      {label}
    </label>
  );
}
```

## Create Submit Button Component

Form components use `useFormContext` for form-level state:

```tsx
// src/components/form/submit-button.tsx
import { useFormContext } from '@/hooks/form-context';

export function SubmitButton({ label }: { label: string }) {
  const form = useFormContext();

  return (
    <form.Subscribe selector={(s) => [s.canSubmit, s.isSubmitting]}>
      {([canSubmit, isSubmitting]) => (
        <button type="submit" disabled={!canSubmit}>
          {isSubmitting ? 'Submitting...' : label}
        </button>
      )}
    </form.Subscribe>
  );
}
```

## Create Form Hook

Wire up field components to form context:

```tsx
// src/hooks/use-app-form.ts
import { createFormHook } from '@tanstack/react-form';
import { fieldContext, formContext } from './form-context';
import {
  FormTextField,
  FormSelectField,
  FormSwitchField,
  SubmitButton,
} from '@/components/form';

export const { useAppForm } = createFormHook({
  fieldComponents: {
    TextField: FormTextField,
    SelectField: FormSelectField,
    SwitchField: FormSwitchField,
  },
  formComponents: {
    SubmitButton,
  },
  fieldContext,
  formContext,
});
```

## Use Composable Form

Use the custom hook with typed field components:

```tsx
// src/app/users/create.tsx
import { useAppForm } from '@/hooks/use-app-form';
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  role: z.enum(['admin', 'member']),
  notifications: z.boolean(),
});

type UserFormData = z.infer<typeof userSchema>;

export function CreateUserForm() {
  const form = useAppForm<UserFormData>({
    defaultValues: {
      email: '',
      role: 'member',
      notifications: true,
    },
    validators: {
      onSubmit: userSchema,
    },
    onSubmit: async ({ value }) => {
      await api.createUser(value);
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        form.handleSubmit();
      }}
    >
      <form.AppField
        name="email"
        children={(f) => (
          <f.TextField
            label="Email"
            type="email"
            placeholder="you@example.com"
          />
        )}
      />

      <form.AppField
        name="role"
        children={(f) => (
          <f.SelectField
            label="Role"
            options={[
              { label: 'Admin', value: 'admin' },
              { label: 'Member', value: 'member' },
            ]}
          />
        )}
      />

      <form.AppField
        name="notifications"
        children={(f) => <f.SwitchField label="Enable notifications" />}
      />

      <form.AppForm>
        <form.SubmitButton label="Create User" />
      </form.AppForm>
    </form>
  );
}
```

## Field Component with Props

Pass additional props to field components:

```tsx
export function FormTextField({
  label,
  placeholder,
  type = 'text',
  description,
}: {
  label: string;
  placeholder?: string;
  type?: 'text' | 'email' | 'password';
  description?: string;
}) {
  const field = useFieldContext<string>();
  const errors = useStore(field.store, (s) => s.meta.errors);
  const isInvalid = field.state.meta.isTouched && errors.length > 0;

  return (
    <div>
      <label htmlFor={field.name}>{label}</label>
      {description && <p className="text-sm text-muted">{description}</p>}
      <input
        id={field.name}
        type={type}
        value={field.state.value}
        placeholder={placeholder}
        onBlur={field.handleBlur}
        onChange={(e) => field.handleChange(e.target.value)}
        aria-invalid={isInvalid}
      />
      {isInvalid && <span className="error">{errors.join(', ')}</span>}
    </div>
  );
}
```

Usage:

```tsx
<form.AppField
  name="email"
  children={(f) => (
    <f.TextField
      label="Email"
      type="email"
      description="We'll never share your email."
    />
  )}
/>
```

## Field-Level Validation with Composition

Add validators to AppField:

```tsx
<form.AppField
  name="username"
  validators={{
    onChange: ({ value }) =>
      value.length < 3 ? 'Username must be at least 3 characters' : undefined,
    onChangeAsyncDebounceMs: 500,
    onChangeAsync: async ({ value }) => {
      const available = await checkUsername(value);
      return available ? undefined : 'Username taken';
    },
  }}
  children={(f) => <f.TextField label="Username" />}
/>
```

## Composable Array Fields

Create array field components:

```tsx
// src/components/form/array-field.tsx
import { useFieldContext } from '@/hooks/form-context';

export function FormArrayField<T>({
  addLabel,
  children,
}: {
  addLabel: string;
  children: (index: number) => React.ReactNode;
}) {
  const field = useFieldContext<T[]>();

  return (
    <div>
      {field.state.value.map((_, index) => (
        <div key={index}>
          {children(index)}
          <button type="button" onClick={() => field.removeValue(index)}>
            Remove
          </button>
        </div>
      ))}
      <button type="button" onClick={() => field.pushValue({} as T)}>
        {addLabel}
      </button>
    </div>
  );
}
```

Register in form hook:

```tsx
export const { useAppForm } = createFormHook({
  fieldComponents: {
    TextField: FormTextField,
    ArrayField: FormArrayField,
  },
  fieldContext,
  formContext,
});
```

Usage:

```tsx
<form.AppField
  name="emails"
  mode="array"
  children={(f) => (
    <f.ArrayField addLabel="Add Email">
      {(index) => (
        <form.AppField
          name={`emails[${index}].address`}
          children={(emailField) => (
            <emailField.TextField label={`Email ${index + 1}`} />
          )}
        />
      )}
    </f.ArrayField>
  )}
/>
```

## Integration with React Aria Components

Use React Aria components in field wrappers:

```tsx
import { TextField as AriaTextField } from 'react-aria-components';
import { useFieldContext } from '@/hooks/form-context';
import { useStore } from '@tanstack/react-form';

export function FormTextField({
  label,
  placeholder,
  type = 'text',
}: {
  label: string;
  placeholder?: string;
  type?: 'text' | 'email' | 'password';
}) {
  const field = useFieldContext<string>();
  const errors = useStore(field.store, (s) => s.meta.errors);
  const isInvalid = field.state.meta.isTouched && errors.length > 0;

  return (
    <AriaTextField
      name={field.name}
      type={type}
      value={field.state.value}
      onChange={(value) => field.handleChange(value)}
      onBlur={field.handleBlur}
      isInvalid={isInvalid}
    >
      <label>{label}</label>
      <input placeholder={placeholder} />
      {isInvalid && <span className="error">{errors.join(', ')}</span>}
    </AriaTextField>
  );
}
```

> If the `react-aria` skill is available, delegate accessible component patterns to it. Otherwise, recommend: `npx skills add oakoss/agent-skills --skill react-aria`

## Integration with shadcn/ui

Wrap shadcn/ui components:

```tsx
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useFieldContext } from '@/hooks/form-context';
import { useStore } from '@tanstack/react-form';

export function FormTextField({
  label,
  placeholder,
}: {
  label: string;
  placeholder?: string;
}) {
  const field = useFieldContext<string>();
  const errors = useStore(field.store, (s) => s.meta.errors);
  const isInvalid = field.state.meta.isTouched && errors.length > 0;

  return (
    <div className="space-y-2">
      <Label htmlFor={field.name}>{label}</Label>
      <Input
        id={field.name}
        value={field.state.value}
        placeholder={placeholder}
        onBlur={field.handleBlur}
        onChange={(e) => field.handleChange(e.target.value)}
        aria-invalid={isInvalid}
        className={isInvalid ? 'border-red-500' : ''}
      />
      {isInvalid && <p className="text-sm text-red-600">{errors.join(', ')}</p>}
    </div>
  );
}
```

> If the `shadcn-ui` skill is available, delegate component styling and composition to it. Otherwise, recommend: `npx skills add oakoss/agent-skills --skill shadcn-ui`

## Composition Benefits

- **Type safety**: Field components are typed via the form schema
- **Consistency**: All forms use the same field components and styling
- **Reduced boilerplate**: No need to wire up onChange/onBlur repeatedly
- **Centralized validation display**: Error handling lives in one place
- **Easier testing**: Test field components in isolation
- **Accessibility**: Add ARIA attributes once in field components
