# Comment Policy

**Default: No comment.** Every comment must earn its place.

Senior developers comment sparingly. If code needs explanation, refactor it first. Comments are a last resort when the code truly cannot speak for itself.

## The Test

Before adding a comment, ask:

1. Can I rename something to make this obvious?
2. Can I extract a well-named function?
3. Can I simplify the logic?
4. Would a competent developer understand this without the comment?

If yes to any, don't comment—fix the code.

## Never Comment

| Don't              | Why                        |
| ------------------ | -------------------------- |
| What code does     | The code already says that |
| Obvious logic      | Insults the reader         |
| Every function     | Types document signatures  |
| To meet some quota | Comments aren't a metric   |
| Commented-out code | That's what git is for     |

```ts
// Noise
// Get user from database
const user = await db.user.findUnique({ where: { id } });

// Pointless JSDoc
/** Returns the user's full name */
function getFullName(user: User): string {
  return `${user.firstName} ${user.lastName}`;
}

// Over-documented
/**
 * Button component
 * @param children - The button content
 * @param onClick - Click handler
 */
function Button({ children, onClick }: ButtonProps); // Types say this already
```

## When Comments Earn Their Place

A comment is justified when it explains something the code **cannot**:

```ts
// WHY this specific value (business context)
// Matches Stripe's webhook retry limit
const MAX_RETRIES = 5;

// WHY this order matters (non-obvious constraint)
// Auth must run before rate-limiter reads user tier
app.use(auth);
app.use(rateLimiter);

// WHAT this regex actually matches (complex pattern)
// Matches ISO 8601 durations: P1D, PT2H30M, P1Y2M3DT4H5M6S
const ISO_DURATION =
  /^P(?:\d+Y)?(?:\d+M)?(?:\d+D)?(?:T(?:\d+H)?(?:\d+M)?(?:\d+S)?)?$/;

// WARNING about non-obvious gotcha
// Returns cents, not dollars
export function getPrice(item: Item): number;

// Link to external context
// See: https://github.com/org/repo/issues/123
```

## JSDoc: Utility Functions vs Components

Different rules for different contexts.

### Utility Functions

JSDoc is valuable when it adds context types cannot:

```ts
// Skip - types are sufficient
function getUserById(id: string): Promise<User | null>;

// Keep - return unit is non-obvious
/**
 * @returns Amount in cents
 */
export function calculateTotal(items: CartItem[]): number;

// Keep - side effect not in signature
/**
 * Deletes user and all associated data. Triggers webhook.
 */
export function deleteUser(id: string): Promise<void>;
```

### Components

**Don't JSDoc the component function.** Document the prop types instead:

```ts
// Noise - don't do this
/**
 * A button component that handles clicks.
 * @param variant - The visual style
 * @param size - The button size
 */
function Button({ variant, size }: ButtonProps);

// Document on the type - defaults and non-obvious behavior
type ButtonProps = {
  /** @default "primary" */
  variant?: 'primary' | 'secondary' | 'destructive';
  /** @default "md" */
  size?: 'sm' | 'md' | 'lg';
  /** Shows spinner and disables interactions */
  loading?: boolean;
};

function Button({ variant = 'primary', size = 'md', loading }: ButtonProps);
```

The prop type IS the documentation.

## TODOs: With Tickets Only

No orphan TODOs. Every TODO needs a ticket so it gets done.

```ts
// TODO(AUTH-456): Add rate limiting
// FIXME(BUG-789): Race condition on logout
```
