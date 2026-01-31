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

## Redundant Entry (WCAG 3.3.7)

Do not require users to re-enter information they have already provided in the same process. Auto-populate from earlier steps or offer a selection from previously entered data.

```tsx
// Multi-step form: carry forward previous answers
function ShippingStep({ billingAddress }: { billingAddress: Address }) {
  const [useSameAddress, setUseSameAddress] = useState(true);

  return (
    <fieldset>
      <legend>Shipping Address</legend>
      <label>
        <input
          type="checkbox"
          checked={useSameAddress}
          onChange={(e) => setUseSameAddress(e.target.checked)}
        />
        Same as billing address
      </label>
      {useSameAddress ? null : <AddressForm />}
    </fieldset>
  );
}
```

## Consistent Help (WCAG 3.2.6)

If a website provides help mechanisms (human contact details, automated chat, self-help links, FAQ), those mechanisms must appear in the same relative order on each page. The help does not need to be on every page, but when present, it must be consistently placed.

```html
<!-- Footer help section: same order on every page -->
<footer>
  <nav aria-label="Help">
    <a href="/faq">FAQ</a>
    <a href="/contact">Contact Us</a>
    <a href="/chat">Live Chat</a>
  </nav>
</footer>
```

## Accessible Authentication (WCAG 3.3.8)

Login flows must not require cognitive function tests (like remembering a password from memory without paste). Allow password managers (do not block paste), support autofill with `autocomplete` attributes, and provide alternatives to CAPTCHAs.

```html
<input type="password" id="password" autocomplete="current-password" />
<!-- Never set autocomplete="off" on password fields -->
<!-- Never block paste events on password fields -->
```
