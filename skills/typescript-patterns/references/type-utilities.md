---
title: Type Utilities
description: Built-in TypeScript utility types for common type transformations
tags:
  [
    Pick,
    Omit,
    Partial,
    Required,
    Record,
    Extract,
    Exclude,
    ReturnType,
    Parameters,
    Awaited,
    utility-types,
  ]
---

# Type Utilities

TypeScript provides built-in utility types for common type transformations. These are globally available without imports.

## Pick and Omit

Extract or exclude specific properties from a type:

```ts
type User = {
  id: string;
  name: string;
  email: string;
  password: string;
  createdAt: Date;
};

type PublicUser = Pick<User, 'id' | 'name' | 'email'>;

type UserWithoutPassword = Omit<User, 'password'>;

type CreateUserInput = Omit<User, 'id' | 'createdAt'>;
```

`Pick` is useful for selecting a subset of properties. `Omit` is better when you want most properties except a few.

## Partial and Required

Make all properties optional or required:

```ts
type UpdateUserInput = Partial<User>;

function updateUser(id: string, updates: UpdateUserInput) {
  // All fields are optional, but type-safe
}

type Config = {
  host?: string;
  port?: number;
  ssl?: boolean;
};

type RequiredConfig = Required<Config>;
```

`Partial` is commonly used for update operations where you only change some fields.

## Record

Create an object type with known keys:

```ts
type Role = 'admin' | 'editor' | 'viewer';

type Permissions = Record<Role, string[]>;

const permissions: Permissions = {
  admin: ['read', 'write', 'delete'],
  editor: ['read', 'write'],
  viewer: ['read'],
};

type ErrorMessages = Record<string, string>;

const errors: ErrorMessages = {
  notFound: 'Resource not found',
  unauthorized: 'Access denied',
};
```

`Record<K, V>` is equivalent to `{ [key in K]: V }` but more concise.

## Extract and Exclude

Filter union types:

```ts
type Status = 'pending' | 'approved' | 'rejected' | 'cancelled';

type ActiveStatus = Exclude<Status, 'cancelled'>;

type EndStatus = Extract<Status, 'approved' | 'rejected'>;

type Primitive = string | number | boolean | null | undefined;

type NonNullable<T> = Exclude<T, null | undefined>;
```

`Exclude` removes types from a union. `Extract` keeps only matching types.

## ReturnType and Parameters

Extract types from functions:

```ts
function createUser(name: string, email: string): User {
  return { id: crypto.randomUUID(), name, email, createdAt: new Date() };
}

type CreateUserReturn = ReturnType<typeof createUser>;

type CreateUserParams = Parameters<typeof createUser>;

type FirstParam = Parameters<typeof createUser>[0];

async function fetchData(): Promise<{ items: string[] }> {
  return { items: [] };
}

type FetchDataReturn = ReturnType<typeof fetchData>;

type UnwrappedReturn = Awaited<FetchDataReturn>;
```

Prefer typing the function return directly rather than extracting it with `ReturnType`.

## Awaited

Unwrap Promise types recursively:

```ts
type PromiseValue = Awaited<Promise<string>>;

type NestedPromise = Awaited<Promise<Promise<number>>>;

async function getData(): Promise<{ user: User }> {
  return { user: { id: '1', name: 'Alice' } };
}

type Data = Awaited<ReturnType<typeof getData>>;

type MaybePromise<T> = T | Promise<T>;

type Resolved<T> = T extends Promise<infer U> ? U : T;

const value: Resolved<MaybePromise<string>> = 'hello';
```

`Awaited` is particularly useful with async functions and Promise-based APIs.

## Readonly and Immutability

Make properties readonly:

```ts
type ImmutableUser = Readonly<User>;

type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

const config: Readonly<{ port: number }> = { port: 3000 };
```

Built-in `Readonly` only applies to top-level properties. Use `DeepReadonly` for nested objects.

## NonNullable

Remove null and undefined from a type:

```ts
type MaybeUser = User | null | undefined;

type DefiniteUser = NonNullable<MaybeUser>;

function processUser(user: User | null) {
  if (user !== null) {
    const definite: NonNullable<typeof user> = user;
  }
}
```

`NonNullable` is equivalent to `Exclude<T, null | undefined>`.

## Combining Utilities

Chain utilities for complex transformations:

```ts
type PartialUpdateUser = Partial<Omit<User, 'id' | 'createdAt'>>;

type RequiredPublicUser = Required<Pick<User, 'id' | 'name'>>;

type ReadonlyCreateInput = Readonly<Omit<User, 'id'>>;

type UserKeys = keyof User;

type OptionalUserKeys = {
  [K in keyof User]?: User[K];
};

type StringKeys<T> = Extract<keyof T, string>;

type UserStringKeys = StringKeys<User>;
```

Combine utilities to express complex type relationships without creating intermediate types.

## ConstructorParameters and InstanceType

Extract types from class constructors:

```ts
class Database {
  constructor(
    public host: string,
    public port: number,
  ) {}
}

type DbParams = ConstructorParameters<typeof Database>;

type DbInstance = InstanceType<typeof Database>;

function createDb(...args: ConstructorParameters<typeof Database>) {
  return new Database(...args);
}
```

These are less commonly used but useful for factory patterns and dependency injection.

## NoInfer

Prevent TypeScript from inferring a type parameter from a specific position:

```ts
function createStreetLight<C extends string>(
  colors: C[],
  defaultColor?: NoInfer<C>,
) {
  // ...
}

createStreetLight(['red', 'yellow', 'green'], 'red'); // OK
createStreetLight(['red', 'yellow', 'green'], 'blue'); // Error

function createConfig<T extends string>(options: T[], initial: NoInfer<T>) {
  return { options, initial };
}
```

`NoInfer<T>` forces the type to be inferred from other positions (e.g., the first argument), preventing widening from the marked position.

## ThisParameterType and OmitThisParameter

Work with function `this` types:

```ts
function greet(this: User, message: string) {
  return `${this.name} says: ${message}`;
}

type GreetThis = ThisParameterType<typeof greet>;

type GreetWithoutThis = OmitThisParameter<typeof greet>;

const boundGreet: GreetWithoutThis = greet.bind(user);
```

Rarely needed in modern TypeScript but useful for working with function contexts.
