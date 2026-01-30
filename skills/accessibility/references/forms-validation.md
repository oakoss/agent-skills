---
title: Forms and Validation
description: Accessible form patterns with label association, error announcements using aria-invalid and role="alert", and required field marking
tags: [forms, validation, labels, aria-invalid, error-handling, screen-reader]
---

# Forms and Validation

## Accessible Form Input

```tsx
function EmailInput({ error }: { error?: string }) {
  return (
    <>
      <label htmlFor="email">Email address *</label>
      <input
        type="email"
        id="email"
        name="email"
        required
        aria-required="true"
        aria-invalid={!!error}
        aria-describedby={error ? 'email-error' : undefined}
      />
      {error && (
        <span id="email-error" role="alert">
          {error}
        </span>
      )}
    </>
  );
}
```

## Form Rules

- Every input needs a visible `<label>` (placeholders are not labels)
- Use `aria-invalid` and `aria-describedby` for errors
- Use `role="alert"` so screen readers announce error messages
- Mark required fields with `aria-required="true"` and visual indicator
- Provide clear instructions before complex forms
- Identify errors in text, not just color
