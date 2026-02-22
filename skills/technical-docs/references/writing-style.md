---
title: Writing Style
description: Voice and tone guidelines, structural standards, formatting rules, error message patterns, inclusive language, and JSDoc/TSDoc patterns for technical documentation
tags:
  [
    style-guide,
    voice,
    tone,
    formatting,
    error-messages,
    inclusive-language,
    jsdoc,
    tsdoc,
  ]
---

## Voice and Tone

### Active Voice

Always prefer active voice:

- Bad: "The function is called by the agent."
- Good: "The agent calls the function."

### Direct and Concise

Avoid fluff. Start with the most important information. Use simple words for complex concepts.

### Inclusive Language

Use gender-neutral pronouns (they/them) or avoid pronouns entirely. Use "users" or "developers" instead of "the user." Avoid obscure jargon unless defined.

## Structural Standards

### The Rule of Three

Limit heading hierarchies to H1, H2, and H3. If you need H4, consider splitting the page.

### Executive Summary

Every page longer than 500 words must start with a brief summary or table of contents.

### Contextual Links

Use descriptive link text:

- Bad: "Click [this link](link) to read more."
- Good: "See the [Authentication Guide](link) for details."

## Formatting Rules

| Element     | Rule                                            |
| ----------- | ----------------------------------------------- |
| Code blocks | Always specify the language                     |
| Bold        | Use for UI elements ("Click **Submit**")        |
| Italics     | Use for technical terms on first use            |
| Lists       | Bulleted for unordered, numbered for sequential |
| Variables   | Meaningful names in code examples               |

## Error Message Guidelines

Model error messages as "Problem, Cause, Solution":

| Component | Example                                    |
| --------- | ------------------------------------------ |
| Problem   | "401 Unauthorized"                         |
| Cause     | "Invalid API Key"                          |
| Solution  | "Check your `.env` file for `AUTH_SECRET`" |

## Documentation Quality Standards

- **Clarity**: Active voice, present tense, direct address
- **Accuracy**: Code examples must be tested and valid
- **Discoverability**: Every page listed in nav config with a descriptive title

## Feature Release Doc Checklist

Every new feature needs these four sections:

1. **Overview**: What it does and why it exists
2. **Configuration**: All env vars, settings, and defaults
3. **Examples**: Quick-start and advanced code blocks
4. **Troubleshooting**: Common errors and fixes

## API Reference Update Flow

1. Update JSDoc/TSDoc in source code
2. Run doc generator (e.g., `make build-docs`)
3. Verify output matches Markdown standards

## JSDoc / TSDoc Patterns

### When to Document

| Document                         | Skip                                        |
| -------------------------------- | ------------------------------------------- |
| Public API functions             | Private/internal helpers                    |
| Non-obvious return values        | Functions where types tell the full story   |
| Side effects not in the type     | Obvious getters and setters                 |
| Complex parameters with defaults | Single-parameter functions with clear names |
| Thrown errors                    | Re-exported types from dependencies         |

### Good JSDoc Examples

```ts
/**
 * @returns Amount in cents, not dollars
 */
export function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

/**
 * Deletes the user and all associated data (posts, comments, sessions).
 * Triggers a `user.deleted` webhook after successful deletion.
 *
 * @throws {NotFoundError} If user does not exist
 * @throws {ForbiddenError} If caller lacks admin role
 */
export async function deleteUser(id: string): Promise<void> {
  // ...
}

/**
 * @param ttl - Cache duration in seconds
 * @default ttl 3600
 */
export function setCacheControl(ttl?: number): void {
  // ...
}
```

### JSDoc to Skip

```ts
// Types already communicate everything here
export function getUserById(id: string): Promise<User | null> {
  return db.user.findUnique({ where: { id } });
}

// Obvious getter
export function getFullName(user: User): string {
  return `${user.firstName} ${user.lastName}`;
}
```

### Component Prop Documentation

Document on the type, not the component function:

```tsx
type AlertProps = {
  /** @default "info" */
  variant?: 'info' | 'warning' | 'error' | 'success';
  /** Dismissible alerts show a close button */
  dismissible?: boolean;
  /** Called when the alert is dismissed; required if `dismissible` is true */
  onDismiss?: () => void;
  children: React.ReactNode;
};

function Alert({
  variant = 'info',
  dismissible,
  onDismiss,
  children,
}: AlertProps) {
  // ...
}
```

### Code Documentation Hierarchy

1. **Self-documenting code first** — rename variables, extract functions, simplify logic
2. **Types second** — let TypeScript signatures communicate contracts
3. **Tests third** — tests document behavior and edge cases
4. **Comments last** — only when the code genuinely cannot explain itself
