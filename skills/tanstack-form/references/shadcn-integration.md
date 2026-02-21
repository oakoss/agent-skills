---
title: shadcn/ui Integration
description: Integrating TanStack Form with shadcn/ui Field, Input, Select, Switch, Checkbox, RadioGroup, and Textarea components
tags:
  [
    shadcn,
    field,
    input,
    select,
    switch,
    checkbox,
    radio-group,
    textarea,
    validation,
    accessibility,
  ]
---

# shadcn/ui Integration

## Component Mapping

| shadcn/ui Component | Form Binding Prop | Change Handler     |
| ------------------- | ----------------- | ------------------ |
| `Input`             | `value`           | `onChange` (event) |
| `Textarea`          | `value`           | `onChange` (event) |
| `Select`            | `value`           | `onValueChange`    |
| `Switch`            | `checked`         | `onCheckedChange`  |
| `Checkbox`          | `checked`         | `onCheckedChange`  |
| `RadioGroup`        | `value`           | `onValueChange`    |

## Field Layout Components

shadcn/ui provides layout primitives that wrap form controls:

| Component          | Purpose                                      |
| ------------------ | -------------------------------------------- |
| `Field`            | Container for a single field with validation |
| `FieldGroup`       | Groups multiple fields together              |
| `FieldLabel`       | Accessible label linked via `htmlFor`        |
| `FieldDescription` | Help text below the control                  |
| `FieldError`       | Displays validation errors                   |
| `FieldSet`         | Groups related fields (checkbox, radio)      |
| `FieldLegend`      | Legend for a fieldset                        |
| `FieldContent`     | Content wrapper for horizontal layouts       |
| `FieldTitle`       | Title within a field (radio cards)           |

## Validation Pattern

Every field follows the same validation display pattern:

```tsx
<form.Field
  name="fieldName"
  children={(field) => {
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;
    return (
      <Field data-invalid={isInvalid}>
        <FieldLabel htmlFor={field.name}>Label</FieldLabel>
        {/* control with aria-invalid={isInvalid} */}
        <FieldDescription>Help text.</FieldDescription>
        {isInvalid && <FieldError errors={field.state.meta.errors} />}
      </Field>
    );
  }}
/>
```

- `data-invalid` on `Field` triggers invalid styling on all children
- `aria-invalid` on the control communicates state to assistive technology
- `FieldError` accepts the `errors` array directly from field meta

## Form Setup

```tsx
import { useForm } from '@tanstack/react-form';
import { z } from 'zod';
import { toast } from 'sonner';

const formSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(10, 'At least 10 characters'),
});

export function BugReportForm() {
  const form = useForm({
    defaultValues: {
      title: '',
      description: '',
    },
    validators: {
      onSubmit: formSchema,
    },
    onSubmit: async ({ value }) => {
      toast.success('Form submitted successfully');
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        form.handleSubmit();
      }}
    >
      <FieldGroup>{/* fields here */}</FieldGroup>
      <Button type="submit">Submit</Button>
    </form>
  );
}
```

## Input

```tsx
<form.Field
  name="title"
  children={(field) => {
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;
    return (
      <Field data-invalid={isInvalid}>
        <FieldLabel htmlFor={field.name}>Bug Title</FieldLabel>
        <Input
          id={field.name}
          name={field.name}
          value={field.state.value}
          onBlur={field.handleBlur}
          onChange={(e) => field.handleChange(e.target.value)}
          aria-invalid={isInvalid}
          placeholder="Login button not working on mobile"
          autoComplete="off"
        />
        <FieldDescription>
          Provide a concise title for your bug report.
        </FieldDescription>
        {isInvalid && <FieldError errors={field.state.meta.errors} />}
      </Field>
    );
  }}
/>
```

## Textarea

Same binding pattern as Input — `value` + `onChange` event:

```tsx
<form.Field
  name="description"
  children={(field) => {
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;
    return (
      <Field data-invalid={isInvalid}>
        <FieldLabel htmlFor={field.name}>Description</FieldLabel>
        <Textarea
          id={field.name}
          name={field.name}
          value={field.state.value}
          onBlur={field.handleBlur}
          onChange={(e) => field.handleChange(e.target.value)}
          aria-invalid={isInvalid}
          placeholder="Describe the issue..."
        />
        {isInvalid && <FieldError errors={field.state.meta.errors} />}
      </Field>
    );
  }}
/>
```

## Select

Uses `onValueChange` (direct value, not event):

```tsx
<form.Field
  name="language"
  children={(field) => {
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;
    return (
      <Field orientation="responsive" data-invalid={isInvalid}>
        <FieldContent>
          <FieldLabel htmlFor="form-select-language">
            Spoken Language
          </FieldLabel>
          <FieldDescription>
            For best results, select the language you speak.
          </FieldDescription>
          {isInvalid && <FieldError errors={field.state.meta.errors} />}
        </FieldContent>
        <Select
          name={field.name}
          value={field.state.value}
          onValueChange={field.handleChange}
        >
          <SelectTrigger
            id="form-select-language"
            aria-invalid={isInvalid}
            className="min-w-[120px]"
          >
            <SelectValue placeholder="Select" />
          </SelectTrigger>
          <SelectContent position="item-aligned">
            <SelectItem value="en">English</SelectItem>
            <SelectItem value="es">Spanish</SelectItem>
            <SelectItem value="fr">French</SelectItem>
          </SelectContent>
        </Select>
      </Field>
    );
  }}
/>
```

## Switch

Uses horizontal `Field` orientation with `FieldContent` wrapper:

```tsx
<form.Field
  name="twoFactor"
  children={(field) => {
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;
    return (
      <Field orientation="horizontal" data-invalid={isInvalid}>
        <FieldContent>
          <FieldLabel htmlFor="form-switch-twoFactor">
            Multi-factor authentication
          </FieldLabel>
          <FieldDescription>
            Enable multi-factor authentication to secure your account.
          </FieldDescription>
          {isInvalid && <FieldError errors={field.state.meta.errors} />}
        </FieldContent>
        <Switch
          id="form-switch-twoFactor"
          name={field.name}
          checked={field.state.value}
          onCheckedChange={field.handleChange}
          aria-invalid={isInvalid}
        />
      </Field>
    );
  }}
/>
```

## Checkbox Group (Array)

Use `mode="array"` with `pushValue`/`removeValue` for multi-select:

```tsx
const tasks = [
  { id: 'bug-fix', label: 'Bug fixes' },
  { id: 'feature', label: 'New features' },
  { id: 'refactor', label: 'Refactoring' },
];

<form.Field
  name="tasks"
  mode="array"
  children={(field) => {
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;
    return (
      <FieldSet>
        <FieldLegend variant="label">Tasks</FieldLegend>
        <FieldDescription>
          Select the task types you want notifications for.
        </FieldDescription>
        <FieldGroup data-slot="checkbox-group">
          {tasks.map((task) => (
            <Field
              key={task.id}
              orientation="horizontal"
              data-invalid={isInvalid}
            >
              <Checkbox
                id={`form-checkbox-${task.id}`}
                name={field.name}
                aria-invalid={isInvalid}
                checked={field.state.value.includes(task.id)}
                onCheckedChange={(checked) => {
                  if (checked) {
                    field.pushValue(task.id);
                  } else {
                    const index = field.state.value.indexOf(task.id);
                    if (index > -1) {
                      field.removeValue(index);
                    }
                  }
                }}
              />
              <FieldLabel
                htmlFor={`form-checkbox-${task.id}`}
                className="font-normal"
              >
                {task.label}
              </FieldLabel>
            </Field>
          ))}
        </FieldGroup>
        {isInvalid && <FieldError errors={field.state.meta.errors} />}
      </FieldSet>
    );
  }}
/>;
```

## RadioGroup

Use `FieldSet`/`FieldLegend` to group radio options:

```tsx
const plans = [
  { id: 'basic', title: 'Basic', description: 'For individuals' },
  { id: 'pro', title: 'Pro', description: 'For teams' },
  { id: 'enterprise', title: 'Enterprise', description: 'For organizations' },
];

<form.Field
  name="plan"
  children={(field) => {
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;
    return (
      <FieldSet>
        <FieldLegend>Plan</FieldLegend>
        <FieldDescription>
          You can upgrade or downgrade your plan at any time.
        </FieldDescription>
        <RadioGroup
          name={field.name}
          value={field.state.value}
          onValueChange={field.handleChange}
        >
          {plans.map((plan) => (
            <FieldLabel key={plan.id} htmlFor={`form-radiogroup-${plan.id}`}>
              <Field orientation="horizontal" data-invalid={isInvalid}>
                <FieldContent>
                  <FieldTitle>{plan.title}</FieldTitle>
                  <FieldDescription>{plan.description}</FieldDescription>
                </FieldContent>
                <RadioGroupItem
                  value={plan.id}
                  id={`form-radiogroup-${plan.id}`}
                  aria-invalid={isInvalid}
                />
              </Field>
            </FieldLabel>
          ))}
        </RadioGroup>
        {isInvalid && <FieldError errors={field.state.meta.errors} />}
      </FieldSet>
    );
  }}
/>;
```

## Key Differences from React Aria

| Concern        | shadcn/ui                                | React Aria                              |
| -------------- | ---------------------------------------- | --------------------------------------- |
| Error display  | `<FieldError errors={...} />`            | `errorMessage` prop on component        |
| Invalid state  | `data-invalid` + `aria-invalid` manually | `isInvalid` prop                        |
| Layout         | `Field` + `FieldContent` composition     | Built into component                    |
| Change handler | Varies per component (see table above)   | Consistent `onChange` with direct value |
| Checkbox array | Manual `pushValue`/`removeValue`         | `CheckboxGroup` with `onChange` array   |
