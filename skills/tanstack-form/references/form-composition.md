---
title: Form Composition
description: Reusable field components with createFormHook, withForm, withFieldGroup, and form contexts
tags:
  [
    composition,
    createFormHook,
    withForm,
    withFieldGroup,
    context,
    reusable,
    fieldComponents,
  ]
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

## Breaking Large Forms with withForm

The `withForm` HOC splits large forms into smaller components while preserving type safety:

```tsx
const PersonalInfoSection = withForm({
  defaultValues: {
    firstName: '',
    lastName: '',
    email: '',
  },
  props: {
    title: 'Personal Info',
  },
  render: function Render({ form, title }) {
    return (
      <div>
        <h2>{title}</h2>
        <form.AppField
          name="firstName"
          children={(field) => <field.TextField label="First Name" />}
        />
        <form.AppField
          name="lastName"
          children={(field) => <field.TextField label="Last Name" />}
        />
      </div>
    );
  },
});

function SignupPage() {
  const form = useAppForm({
    defaultValues: { firstName: '', lastName: '', email: '' },
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
      <PersonalInfoSection form={form} title="Your Details" />
      <form.AppForm>
        <form.SubmitButton label="Sign Up" />
      </form.AppForm>
    </form>
  );
}
```

The `defaultValues` in `withForm` are for type-checking only. The parent form's `defaultValues` are what matter.

## Reusable Field Groups with withFieldGroup

The `withFieldGroup` HOC groups related fields that share validation logic and can be reused across forms:

```tsx
import { useStore } from '@tanstack/react-form';

const { useAppForm, withForm, withFieldGroup } = createFormHook({
  fieldComponents: { TextField, ErrorInfo },
  formComponents: { SubmitButton },
  fieldContext,
  formContext,
});

type PasswordFields = {
  password: string;
  confirm_password: string;
};

const PasswordFieldGroup = withFieldGroup({
  defaultValues: {
    password: '',
    confirm_password: '',
  } satisfies PasswordFields,
  props: {
    title: 'Password',
  },
  render: function Render({ group, title }) {
    const password = useStore(group.store, (state) => state.values.password);

    return (
      <div>
        <h3>{title}</h3>
        <group.AppField name="password">
          {(field) => <field.TextField label="Password" />}
        </group.AppField>
        <group.AppField
          name="confirm_password"
          validators={{
            onChangeListenTo: ['password'],
            onChange: ({ value }) => {
              if (value !== group.getFieldValue('password')) {
                return 'Passwords do not match';
              }
              return undefined;
            },
          }}
        >
          {(field) => (
            <div>
              <field.TextField label="Confirm Password" />
              <field.ErrorInfo />
            </div>
          )}
        </group.AppField>
      </div>
    );
  },
});
```

Use the group by passing `form` and a `fields` path to map to nested values:

```tsx
<PasswordFieldGroup form={form} fields="credentials" title="Set Password" />
```

Field groups work with arrays too:

```tsx
<form.Field name="accounts" mode="array">
  {(field) =>
    field.state.value.map((account, i) => (
      <PasswordFieldGroup
        key={i}
        form={form}
        fields={`accounts[${i}]`}
        title={`Account ${i + 1}`}
      />
    ))
  }
</form.Field>
```
