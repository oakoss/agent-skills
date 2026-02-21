---
title: React Aria Integration
description: Integrating TanStack Form with React Aria components for accessible form controls
tags:
  [
    react-aria,
    TextField,
    NumberField,
    Select,
    ComboBox,
    Switch,
    Checkbox,
    RadioGroup,
    DatePicker,
    CheckboxGroup,
  ]
---

# React Aria Integration

## Component Mapping

| Form Control  | React Aria    | Binding Prop  | Change Handler            |
| ------------- | ------------- | ------------- | ------------------------- |
| Text input    | `TextField`   | `value`       | `onChange` (direct value) |
| Numeric input | `NumberField` | `value`       | `onChange` (direct value) |
| Dropdown      | `Select`      | `selectedKey` | `onSelectionChange`       |
| Autocomplete  | `ComboBox`    | `selectedKey` | `onSelectionChange`       |
| Boolean       | `Checkbox`    | `isSelected`  | `onChange`                |
| Toggle        | `Switch`      | `isSelected`  | `onChange`                |
| Single select | `RadioGroup`  | `value`       | `onChange`                |
| Date          | `DatePicker`  | `value`       | `onChange`                |

React Aria components handle validation display via `isInvalid` and `errorMessage` props directly — no separate error component needed.

## Text Input

```tsx
<form.Field
  name="username"
  children={(field) => {
    const isInvalid = field.state.meta.isTouched && !field.state.meta.isValid;
    return (
      <TextField
        label="Username"
        value={field.state.value}
        onBlur={field.handleBlur}
        onChange={(value) => field.handleChange(value)}
        isInvalid={isInvalid}
        errorMessage={
          isInvalid ? field.state.meta.errors.join(', ') : undefined
        }
      />
    );
  }}
/>
```

## Select

```tsx
<form.Field
  name="language"
  children={(field) => (
    <Select
      label="Language"
      selectedKey={field.state.value}
      onSelectionChange={(key) => field.handleChange(key as string)}
    >
      <SelectItem id="en">English</SelectItem>
      <SelectItem id="es">Spanish</SelectItem>
      <SelectItem id="fr">French</SelectItem>
    </Select>
  )}
/>
```

## Switch

```tsx
<form.Field
  name="notifications"
  children={(field) => (
    <Switch isSelected={field.state.value} onChange={field.handleChange}>
      Enable notifications
    </Switch>
  )}
/>
```

## Checkbox

```tsx
<form.Field
  name="terms"
  children={(field) => (
    <Checkbox isSelected={field.state.value} onChange={field.handleChange}>
      Accept terms and conditions
    </Checkbox>
  )}
/>
```

## Radio Group

```tsx
const plans = [
  { id: 'basic', title: 'Basic', description: 'For individuals' },
  { id: 'pro', title: 'Pro', description: 'For teams' },
];

<form.Field
  name="plan"
  children={(field) => (
    <RadioGroup
      label="Plan"
      value={field.state.value}
      onChange={field.handleChange}
    >
      {plans.map((plan) => (
        <Radio key={plan.id} value={plan.id}>
          {plan.title}
        </Radio>
      ))}
    </RadioGroup>
  )}
/>;
```

## Checkbox Group

Use `mode="array"` with `CheckboxGroup` for multi-select checkbox patterns:

```tsx
<form.Field
  name="features"
  mode="array"
  children={(field) => (
    <CheckboxGroup
      label="Features"
      value={field.state.value}
      onChange={field.handleChange}
    >
      {features.map((feature) => (
        <Checkbox key={feature.id} value={feature.id}>
          {feature.label}
        </Checkbox>
      ))}
    </CheckboxGroup>
  )}
/>
```

## Key Differences from shadcn/ui

| Concern        | React Aria                              | shadcn/ui                                |
| -------------- | --------------------------------------- | ---------------------------------------- |
| Error display  | `isInvalid` + `errorMessage` props      | `<FieldError errors={...} />` component  |
| Invalid state  | `isInvalid` prop                        | `data-invalid` + `aria-invalid` manually |
| Layout         | Built into component                    | `Field` + `FieldContent` composition     |
| Change handler | Consistent `onChange` with direct value | Varies per component                     |
| Checkbox array | `CheckboxGroup` with `onChange` array   | Manual `pushValue`/`removeValue`         |
