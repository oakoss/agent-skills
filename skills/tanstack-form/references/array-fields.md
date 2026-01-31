---
title: Array Fields
description: Dynamic field arrays with add, remove, move, and swap operations
tags: [array, pushValue, removeValue, swapValues, moveValue, dynamic]
---

# Array Fields

## Basic Array Field

Use `mode="array"` to manage dynamic lists:

```tsx
import { useForm } from '@tanstack/react-form';

function HobbiesForm() {
  const form = useForm({
    defaultValues: {
      hobbies: [] as Array<{ name: string; description: string }>,
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        form.handleSubmit();
      }}
    >
      <form.Field name="hobbies" mode="array">
        {(hobbiesField) => (
          <div>
            <h3>Hobbies</h3>
            {!hobbiesField.state.value.length ? (
              <p>No hobbies added yet.</p>
            ) : (
              hobbiesField.state.value.map((_, index) => (
                <div key={index}>
                  <form.Field
                    name={`hobbies[${index}].name`}
                    children={(field) => (
                      <div>
                        <label htmlFor={field.name}>Name:</label>
                        <input
                          id={field.name}
                          value={field.state.value}
                          onChange={(e) => field.handleChange(e.target.value)}
                        />
                      </div>
                    )}
                  />
                  <button
                    type="button"
                    onClick={() => hobbiesField.removeValue(index)}
                  >
                    Remove
                  </button>
                </div>
              ))
            )}
            <button
              type="button"
              onClick={() =>
                hobbiesField.pushValue({
                  name: '',
                  description: '',
                })
              }
            >
              Add Hobby
            </button>
          </div>
        )}
      </form.Field>
    </form>
  );
}
```

## Array Field Methods

| Method                          | Description               |
| ------------------------------- | ------------------------- |
| `pushValue(value)`              | Add item to end of array  |
| `removeValue(index)`            | Remove item at index      |
| `insertValue(index, value)`     | Insert item at index      |
| `replaceValue(index, value)`    | Replace item at index     |
| `swapValues(indexA, indexB)`    | Swap two items            |
| `moveValue(fromIndex, toIndex)` | Move item to new position |
| `clearValues()`                 | Remove all items          |

### Push Value

```tsx
<button type="button" onClick={() => field.pushValue({ name: '', email: '' })}>
  Add Member
</button>
```

### Insert Value

```tsx
<button
  type="button"
  onClick={() => field.insertValue(0, { name: 'New Item', email: '' })}
>
  Insert at Start
</button>
```

### Swap Values

```tsx
<button
  type="button"
  onClick={() => field.swapValues(index, index + 1)}
  disabled={index >= field.state.value.length - 1}
>
  Move Down
</button>
```

### Move Value

```tsx
<button type="button" onClick={() => field.moveValue(index, 0)}>
  Move to Top
</button>
```

## Array Field with Validation

Validate individual array items:

```tsx
import { z } from 'zod';

const emailSchema = z.string().email();

<form.Field name="members" mode="array">
  {(field) => (
    <div>
      {field.state.value.map((_, index) => (
        <form.Field
          key={index}
          name={`members[${index}].email`}
          validators={{
            onChange: emailSchema,
          }}
          children={(emailField) => (
            <div>
              <input
                value={emailField.state.value}
                onChange={(e) => emailField.handleChange(e.target.value)}
              />
              {emailField.state.meta.isTouched &&
                emailField.state.meta.errors.length > 0 && (
                  <em>{emailField.state.meta.errors.join(', ')}</em>
                )}
            </div>
          )}
        />
      ))}
      <button type="button" onClick={() => field.pushValue({ email: '' })}>
        Add Email
      </button>
    </div>
  )}
</form.Field>;
```

Validate the array as a whole:

```tsx
const membersSchema = z
  .array(
    z.object({
      name: z.string().min(1),
      email: z.string().email(),
    }),
  )
  .min(1, 'At least one member is required')
  .max(10, 'Maximum 10 members allowed');

const form = useForm({
  defaultValues: {
    members: [],
  },
  validators: {
    onSubmit: z.object({
      members: membersSchema,
    }),
  },
});
```

## Stable Keys for Array Items

Use stable keys to avoid React reconciliation issues:

```tsx
type Hobby = {
  id: string;
  name: string;
};

<form.Field name="hobbies" mode="array">
  {(field) => (
    <div>
      {field.state.value.map((hobby) => (
        <div key={hobby.id}>
          <form.Field
            name={`hobbies[${field.state.value.indexOf(hobby)}].name`}
            children={(subField) => (
              <input
                value={subField.state.value}
                onChange={(e) => subField.handleChange(e.target.value)}
              />
            )}
          />
          <button
            type="button"
            onClick={() => field.removeValue(field.state.value.indexOf(hobby))}
          >
            Remove
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() =>
          field.pushValue({
            id: crypto.randomUUID(),
            name: '',
          })
        }
      >
        Add Hobby
      </button>
    </div>
  )}
</form.Field>;
```

## Reorderable List

```tsx
<form.Field name="tasks" mode="array">
  {(field) => (
    <div>
      {field.state.value.map((_, index) => (
        <div key={index}>
          <form.Field
            name={`tasks[${index}].title`}
            children={(subField) => (
              <input
                value={subField.state.value}
                onChange={(e) => subField.handleChange(e.target.value)}
              />
            )}
          />
          <button
            type="button"
            onClick={() => field.moveValue(index, index - 1)}
            disabled={index === 0}
          >
            Move Up
          </button>
          <button
            type="button"
            onClick={() => field.moveValue(index, index + 1)}
            disabled={index >= field.state.value.length - 1}
          >
            Move Down
          </button>
          <button type="button" onClick={() => field.removeValue(index)}>
            Remove
          </button>
        </div>
      ))}
      <button type="button" onClick={() => field.pushValue({ title: '' })}>
        Add Task
      </button>
    </div>
  )}
</form.Field>
```

## Nested Arrays

Arrays within arrays:

```tsx
type Section = {
  title: string;
  items: Array<{ name: string }>;
};

<form.Field name="sections" mode="array">
  {(sectionsField) => (
    <div>
      {sectionsField.state.value.map((_, sectionIndex) => (
        <div key={sectionIndex}>
          <form.Field
            name={`sections[${sectionIndex}].title`}
            children={(field) => (
              <input
                value={field.state.value}
                onChange={(e) => field.handleChange(e.target.value)}
              />
            )}
          />

          <form.Field name={`sections[${sectionIndex}].items`} mode="array">
            {(itemsField) => (
              <div>
                {itemsField.state.value.map((_, itemIndex) => (
                  <div key={itemIndex}>
                    <form.Field
                      name={`sections[${sectionIndex}].items[${itemIndex}].name`}
                      children={(field) => (
                        <input
                          value={field.state.value}
                          onChange={(e) => field.handleChange(e.target.value)}
                        />
                      )}
                    />
                    <button
                      type="button"
                      onClick={() => itemsField.removeValue(itemIndex)}
                    >
                      Remove Item
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => itemsField.pushValue({ name: '' })}
                >
                  Add Item
                </button>
              </div>
            )}
          </form.Field>

          <button
            type="button"
            onClick={() => sectionsField.removeValue(sectionIndex)}
          >
            Remove Section
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() => sectionsField.pushValue({ title: '', items: [] })}
      >
        Add Section
      </button>
    </div>
  )}
</form.Field>;
```

## Array Field Notes

- Use `mode="array"` on the parent field to enable array methods
- Always provide a stable `key` prop when mapping array items
- Use template syntax for nested field names: `items[${index}].name`
- Array methods (`pushValue`, `removeValue`, etc.) are available on the array field, not sub-fields
- Validate individual items with field-level validators, or the entire array with form-level validators
