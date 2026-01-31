---
title: Code Slop
description: Detecting and fixing AI-generated code smells including over-commenting, unnecessary abstractions, verbose naming, and defensive over-engineering
tags:
  [
    code,
    refactoring,
    over-engineering,
    comments,
    naming,
    abstractions,
    code-review,
    patterns,
  ]
---

# Code Slop

AI-generated code has its own set of tells, distinct from prose slop. Research shows that 76% of developers say AI-generated code needs refactoring, and code duplication ("copy/pasted" lines) rose from 8.3% to 12.3% between 2021 and 2024 as AI coding tools gained adoption.

## Over-Commenting

The strongest code slop signal. LLMs add formal docstrings to trivial functions and line-by-line narration that restates the code.

### The Tell

```ts
/**
 * Retrieves a user by their unique identifier from the database.
 * @param id - The unique identifier of the user to retrieve.
 * @returns A promise that resolves to the user object, or null if not found.
 */
async function getUserById(id: string): Promise<User | null> {
  // Find the user in the database using the provided ID
  const user = await db.user.findUnique({
    // Search by the id field
    where: { id },
  });
  // Return the found user or null
  return user;
}
```

### The Fix

```ts
async function getUserById(id: string): Promise<User | null> {
  return db.user.findUnique({ where: { id } });
}
```

The types already document the signature. The function name describes the behavior. The implementation is one line. Zero comments needed.

### When Comments Are Justified in AI Code

Keep comments that explain **why**, not **what**:

```ts
// Stripe webhooks retry up to 3 times with exponential backoff
const MAX_RETRIES = 3;

// Auth middleware must run before rate limiter reads user tier
app.use(auth);
app.use(rateLimiter);
```

## Unnecessary Abstractions

LLMs over-apply design patterns. A 20-line script becomes a class with three helper methods and an abstract base class. Factories and singletons appear for problems that do not need them.

### The Tell

```ts
interface DataProcessor {
  process(data: unknown): Promise<void>;
}

class UserDataProcessor implements DataProcessor {
  private readonly validator: DataValidator;
  private readonly transformer: DataTransformer;
  private readonly persister: DataPersister;

  constructor(
    validator: DataValidator,
    transformer: DataTransformer,
    persister: DataPersister,
  ) {
    this.validator = validator;
    this.transformer = transformer;
    this.persister = persister;
  }

  async process(data: unknown): Promise<void> {
    const validated = await this.validator.validate(data);
    const transformed = await this.transformer.transform(validated);
    await this.persister.persist(transformed);
  }
}
```

### The Fix

If there is only one implementation of each interface, the abstraction is premature:

```ts
async function processUserData(data: unknown): Promise<void> {
  const user = userSchema.parse(data);
  const normalized = { ...user, email: user.email.toLowerCase() };
  await db.user.create({ data: normalized });
}
```

### The Rule

Introduce abstractions when you have two or more concrete implementations, not before. LLMs generate "extensible" code for requirements that do not exist.

## Verbose Naming

AI-generated code uses longer, more explicitly descriptive names than human developers. Research shows AI averages 19 characters per function name versus 14 for humans.

### The Tell

```ts
const retrievedUserFromDatabase = await getUserById(userId);
const isUserCurrentlyAuthenticated = session.isValid();
const formattedDateTimeString = date.toISOString();
const filteredActiveUsersList = users.filter((u) => u.active);
```

### The Fix

```ts
const user = await getUserById(userId);
const isAuthenticated = session.isValid();
const timestamp = date.toISOString();
const activeUsers = users.filter((u) => u.active);
```

Context eliminates the need for every noun in the name. In a function called `getUser`, the variable holding the result does not need "retrieved" or "fromDatabase."

## Defensive Over-Engineering

LLMs wrap every operation in try-catch, validate inputs that the type system already guarantees, and add null checks for values that cannot be null.

### The Tell

```ts
async function getUser(id: string): Promise<User | null> {
  try {
    if (!id) {
      throw new Error('User ID is required');
    }
    if (typeof id !== 'string') {
      throw new Error('User ID must be a string');
    }
    const user = await db.user.findUnique({ where: { id } });
    if (!user) {
      return null;
    }
    return user;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}
```

### The Fix

```ts
async function getUser(id: string): Promise<User | null> {
  return db.user.findUnique({ where: { id } });
}
```

TypeScript enforces `id` is a string at compile time. The `findUnique` call already returns `null` when no record exists. The try-catch logs and re-throws, which is worse than letting the error propagate naturally.

### When Defensive Code Is Justified

- At API boundaries where input comes from untrusted sources
- Around third-party service calls that have known failure modes
- In error recovery paths where you need cleanup logic

## Code Duplication

LLMs generate code without awareness of the existing codebase. The same utility function gets reimplemented in multiple files with minor variations.

### Detection

```bash
# Look for suspiciously similar function signatures
grep -rn "function formatDate\|function formatTimestamp\|function dateToString" src/
```

### The Fix

Extract duplicated logic into a shared utility. LLMs resist this because each generation is context-independent; they do not know what already exists elsewhere.

## Statistical Regularity

Human code varies in style across a file. Some functions are terse, others verbose. AI-generated code maintains eerily consistent patterns:

- Every function has exactly the same comment structure
- All error messages follow the same template: "Error [verb]ing [noun]: [error]"
- Import blocks are identically organized across every file
- Every function is roughly the same length

### The Fix

Inconsistency is not a problem to solve. If the code works and is readable, do not impose artificial uniformity. The tell is when uniformity already exists across code that should show natural variation.

## Code Slop Review Checklist

| Check          | Question                                                          | Action if Yes                                           |
| -------------- | ----------------------------------------------------------------- | ------------------------------------------------------- |
| Comments       | Does the comment restate what the code does?                      | Delete the comment                                      |
| Comments       | Is there a docstring on a function whose name + types explain it? | Delete the docstring                                    |
| Abstractions   | Is there only one implementation of this interface?               | Inline it; remove the interface                         |
| Abstractions   | Is this factory/builder/strategy pattern needed?                  | Replace with a plain function                           |
| Naming         | Is the variable name longer than 25 characters?                   | Shorten using context                                   |
| Naming         | Does the name include the type ("userString", "dateObject")?      | Remove the type suffix                                  |
| Error handling | Does this try-catch just log and re-throw?                        | Remove the try-catch                                    |
| Error handling | Is this null check on a value that cannot be null?                | Remove the check                                        |
| Duplication    | Does similar logic exist elsewhere in the codebase?               | Extract to a shared function                            |
| Structure      | Are all functions the same length and shape?                      | Natural variation is fine; forced uniformity is a smell |

## Model Collapse in Iterative AI Edits

When AI assistants repeatedly modify code without human oversight, each iteration introduces small deviations from best practices. Variable names become more generic, comments replace clear code, functions grow longer, and domain concepts blur. This is called "model collapse" in codebases.

The defense: after every AI-assisted editing session, do a human review pass specifically looking for:

- Generic names that replaced domain-specific ones (e.g., `data` replacing `invoice`)
- New comments that explain obvious code
- Increased function length
- Lost abstractions that were previously correct
