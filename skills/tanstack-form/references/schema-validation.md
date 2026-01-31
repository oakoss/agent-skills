---
title: Schema Validation
description: Standard Schema integration with Zod, Valibot, ArkType, and Yup
tags: [zod, valibot, arktype, yup, standard-schema, form-level]
---

# Schema Validation

## Standard Schema Support

TanStack Form natively supports Standard Schema libraries:

| Library | Minimum Version |
| ------- | --------------- |
| Zod     | v3.24.0+        |
| Valibot | v1.0.0+         |
| ArkType | v2.1.20+        |
| Yup     | v1.7.0+         |

No adapter needed - pass schemas directly to validators.

## Zod

### Field-Level Validation

```tsx
import { z } from 'zod';

const emailSchema = z.string().email();

<form.Field
  name="email"
  validators={{
    onChange: emailSchema,
  }}
  children={(field) => (
    <input
      value={field.state.value}
      onChange={(e) => field.handleChange(e.target.value)}
    />
  )}
/>;
```

### Form-Level Schema

```tsx
const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  age: z.number().min(13),
});

const form = useForm({
  defaultValues: {
    email: '',
    password: '',
    age: 0,
  },
  validators: {
    onSubmit: userSchema,
  },
});
```

### Password Confirmation

```tsx
const passwordSchema = z
  .object({
    password: z.string().min(8),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

const form = useForm({
  defaultValues: {
    password: '',
    confirmPassword: '',
  },
  validators: {
    onSubmit: passwordSchema,
  },
});
```

### Enum Validation

```tsx
const planSchema = z.enum(['basic', 'pro', 'enterprise']);

<form.Field
  name="plan"
  validators={{
    onChange: planSchema,
  }}
/>;
```

### Array Validation

```tsx
const emailsSchema = z
  .array(z.object({ address: z.string().email() }))
  .min(1, 'At least one email is required')
  .max(5, 'Maximum 5 emails allowed');

const form = useForm({
  defaultValues: {
    emails: [],
  },
  validators: {
    onSubmit: z.object({ emails: emailsSchema }),
  },
});
```

### Custom Error Messages

```tsx
const emailSchema = z.string().email('Please enter a valid email address');

<form.Field
  name="email"
  validators={{
    onChange: ({ value }) => {
      const result = emailSchema.safeParse(value);
      if (!result.success) {
        return result.error.errors[0].message;
      }
      return undefined;
    },
  }}
/>;
```

## Valibot

```tsx
import * as v from 'valibot';

const emailSchema = v.pipe(v.string(), v.email());

<form.Field
  name="email"
  validators={{
    onChange: emailSchema,
  }}
/>;
```

Form-level:

```tsx
const userSchema = v.object({
  email: v.pipe(v.string(), v.email()),
  password: v.pipe(v.string(), v.minLength(8)),
});

const form = useForm({
  defaultValues: {
    email: '',
    password: '',
  },
  validators: {
    onSubmit: userSchema,
  },
});
```

## ArkType

```tsx
import { type } from 'arktype';

const emailType = type('string.email');

<form.Field
  name="email"
  validators={{
    onChange: emailType,
  }}
/>;
```

Form-level:

```tsx
const userType = type({
  email: 'string.email',
  'password?': 'string>=8',
});

const form = useForm({
  defaultValues: {
    email: '',
    password: '',
  },
  validators: {
    onSubmit: userType,
  },
});
```

## Yup

```tsx
import * as yup from 'yup';

const emailSchema = yup.string().email().required();

<form.Field
  name="email"
  validators={{
    onChange: emailSchema,
  }}
/>;
```

Form-level:

```tsx
const userSchema = yup.object({
  email: yup.string().email().required(),
  password: yup.string().min(8).required(),
});

const form = useForm({
  defaultValues: {
    email: '',
    password: '',
  },
  validators: {
    onSubmit: userSchema,
  },
});
```

## Zod Advanced Patterns

### Conditional Validation

```tsx
const formSchema = z
  .object({
    accountType: z.enum(['personal', 'business']),
    companyName: z.string().optional(),
    taxId: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.accountType === 'business') {
        return !!data.companyName && !!data.taxId;
      }
      return true;
    },
    {
      message: 'Company name and tax ID are required for business accounts',
      path: ['companyName'],
    },
  );
```

### Transform and Validate

```tsx
const schema = z
  .string()
  .transform((val) => val.trim())
  .pipe(z.string().min(3));

<form.Field
  name="username"
  validators={{
    onChange: schema,
  }}
/>;
```

### Nested Objects

```tsx
const addressSchema = z.object({
  street: z.string().min(1),
  city: z.string().min(1),
  postalCode: z.string().regex(/^\d{5}$/),
});

const userSchema = z.object({
  name: z.string().min(1),
  address: addressSchema,
});

const form = useForm({
  defaultValues: {
    name: '',
    address: {
      street: '',
      city: '',
      postalCode: '',
    },
  },
  validators: {
    onSubmit: userSchema,
  },
});
```

### Union Types

```tsx
const paymentSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('card'),
    cardNumber: z.string().regex(/^\d{16}$/),
    cvv: z.string().regex(/^\d{3}$/),
  }),
  z.object({
    type: z.literal('bank'),
    accountNumber: z.string(),
    routingNumber: z.string(),
  }),
]);
```

### Coercion

```tsx
const schema = z.object({
  age: z.coerce.number().min(13),
  acceptTerms: z.coerce.boolean(),
});

const form = useForm({
  defaultValues: {
    age: 0,
    acceptTerms: false,
  },
  validators: {
    onSubmit: schema,
  },
});
```

## Validation Strategy Comparison

| Strategy       | When to Use                              | Performance |
| -------------- | ---------------------------------------- | ----------- |
| Form-level     | Simple forms, submit-only validation     | Best        |
| Field-level    | Real-time feedback, complex dependencies | Good        |
| Mixed          | Most forms (form schema + field async)   | Good        |
| Schema + async | Server-side checks + client validation   | Slower      |

## Best Practices

- Use form-level schemas for simple validation
- Use field-level validators for async checks (username availability, etc.)
- Combine both: form schema for structure, field async for server validation
- Always validate server-side too, never trust client-only validation
- Use `.safeParse()` to extract custom error messages from schemas
- Coerce types when working with HTML form inputs (always return strings)
