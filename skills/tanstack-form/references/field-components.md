---
title: Field Components
description: React Aria component integration, input type patterns, field listeners for side effects, and checkbox group handling
tags:
  [
    react-aria,
    TextField,
    Select,
    Switch,
    Checkbox,
    RadioGroup,
    listeners,
    CheckboxGroup,
  ]
---

# Field Components

## React Aria Component Integration

| Component     | React Aria    | Purpose         |
| ------------- | ------------- | --------------- |
| `TextField`   | `TextField`   | Text input      |
| `NumberField` | `NumberField` | Numeric input   |
| `Select`      | `Select`      | Dropdown select |
| `ComboBox`    | `ComboBox`    | Autocomplete    |
| `Checkbox`    | `Checkbox`    | Boolean toggle  |
| `Switch`      | `Switch`      | Toggle switch   |
| `RadioGroup`  | `RadioGroup`  | Single select   |
| `DatePicker`  | `DatePicker`  | Date selection  |

## Input Types

### Text Input

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

### Select

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

### Switch

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

### Checkbox

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

### Radio Group

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

## Field Listeners

Use `listeners` to trigger side effects when field values change:

```tsx
<form.Field
  name="country"
  listeners={{
    onChange: ({ value }) => {
      form.setFieldValue('province', '');
    },
  }}
  children={(field) => (
    <Select
      label="Country"
      selectedKey={field.state.value}
      onSelectionChange={(key) => field.handleChange(key as string)}
    >
      {countries.map((c) => (
        <SelectItem key={c.code} id={c.code}>
          {c.name}
        </SelectItem>
      ))}
    </Select>
  )}
/>

<form.Field
  name="province"
  children={(field) => (
    <Select
      label="Province"
      selectedKey={field.state.value}
      onSelectionChange={(key) => field.handleChange(key as string)}
    >
      {getProvinces(form.getFieldValue('country')).map((p) => (
        <SelectItem key={p.code} id={p.code}>
          {p.name}
        </SelectItem>
      ))}
    </Select>
  )}
/>
```

Listeners are for side effects (resetting dependent fields, fetching data). For validation that depends on other fields, use `onChangeListenTo` in validators instead.

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
