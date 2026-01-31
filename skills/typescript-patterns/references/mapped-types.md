---
title: Mapped Types
description: Transform object properties with mapped types, key remapping, and template literals
tags: [mapped-types, key-remapping, template-literals, modifiers, keyof, in]
---

# Mapped Types

Mapped types transform all properties of an existing type.

## Basic Mapped Types

Iterate over keys with `in keyof`:

```ts
type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};

type User = {
  id: string;
  name: string;
};

type ReadonlyUser = Readonly<User>;

type Partial<T> = {
  [K in keyof T]?: T[K];
};

type PartialUser = Partial<User>;

type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};

type NullableUser = Nullable<User>;
```

Mapped types iterate over each property of the source type.

## Adding and Removing Modifiers

Use `+` and `-` to add or remove `readonly` and `?`:

```ts
type Mutable<T> = {
  -readonly [K in keyof T]: T[K];
};

type Required<T> = {
  [K in keyof T]-?: T[K];
};

type Optional<T> = {
  +readonly [K in keyof T]?: T[K];
};

type Config = {
  readonly host: string;
  readonly port?: number;
};

type MutableConfig = Mutable<Config>;
type RequiredConfig = Required<Config>;
```

Omit the `+` or `-` prefix to leave modifiers unchanged.

## Key Remapping with as

Rename keys using `as` and template literals:

```ts
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<User>;

type Setters<T> = {
  [K in keyof T as `set${Capitalize<string & K>}`]: (value: T[K]) => void;
};

type UserSetters = Setters<User>;

type Events<T> = {
  [K in keyof T as `on${Capitalize<string & K>}Change`]: (value: T[K]) => void;
};

type UserEvents = Events<User>;
```

Key remapping transforms property names during iteration.

## Filtering Properties

Use `never` to exclude keys:

```ts
type RemoveReadonly<T> = {
  [K in keyof T as T[K] extends Function ? never : K]: T[K];
};

type User = {
  id: string;
  name: string;
  save: () => void;
};

type UserData = RemoveReadonly<User>;

type PickByType<T, ValueType> = {
  [K in keyof T as T[K] extends ValueType ? K : never]: T[K];
};

type StringProps = PickByType<User, string>;

type OmitByType<T, ValueType> = {
  [K in keyof T as T[K] extends ValueType ? never : K]: T[K];
};

type NonStringProps = OmitByType<User, string>;
```

`never` keys are automatically removed from the resulting type.

## Template Literal Types

Combine strings at the type level:

```ts
type Direction = 'top' | 'right' | 'bottom' | 'left';
type Size = 'sm' | 'md' | 'lg';

type Margin = `margin${Capitalize<Direction>}`;

type PaddingSize = `padding-${Size}`;

type CSSProperty = `${Direction}-${Size}`;

type EventName<T extends string> = `on${Capitalize<T>}`;

type Events = EventName<'click' | 'scroll' | 'resize'>;
```

Template literal types work like template strings but at the type level.

## Built-in String Manipulation

TypeScript provides built-in string utility types:

```ts
type Uppercased = Uppercase<'hello'>;

type Lowercased = Lowercase<'HELLO'>;

type Capitalized = Capitalize<'hello'>;

type Uncapitalized = Uncapitalize<'Hello'>;

type Route = '/users' | '/posts' | '/comments';
type RouteName = Capitalize<Uppercase<Route>>;
```

These are intrinsic types implemented by the compiler.

## Nested Mapped Types

Transform nested object properties:

```ts
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

type Config = {
  server: {
    host: string;
    port: number;
  };
  cache: {
    ttl: number;
  };
};

type PartialConfig = DeepPartial<Config>;
```

Recursive mapped types handle arbitrarily nested structures.

## Conditional Property Types

Change property types conditionally:

```ts
type Stringify<T> = {
  [K in keyof T]: T[K] extends string ? T[K] : string;
};

type Numberify<T> = {
  [K in keyof T]: T[K] extends number ? T[K] : number;
};

type Promisify<T> = {
  [K in keyof T]: Promise<T[K]>;
};

type AsyncUser = Promisify<User>;

type MaybeNull<T> = {
  [K in keyof T]: T[K] | null;
};
```

Combine mapped types with conditional types for powerful transformations.

## Union to Intersection

Convert union types to intersections:

```ts
type UnionToIntersection<U> = (
  U extends unknown ? (k: U) => void : never
) extends (k: infer I) => void
  ? I
  : never;

type Union = { a: string } | { b: number };
type Intersection = UnionToIntersection<Union>;

type Merge<T, U> = {
  [K in keyof T | keyof U]: K extends keyof T
    ? K extends keyof U
      ? T[K] | U[K]
      : T[K]
    : K extends keyof U
      ? U[K]
      : never;
};

type A = { a: string; b: number };
type B = { b: string; c: boolean };
type C = Merge<A, B>;
```

Advanced type manipulation for complex scenarios.

## Pick and Omit Implementation

Implement utility types with mapped types:

```ts
type Pick<T, K extends keyof T> = {
  [P in K]: T[P];
};

type Omit<T, K extends keyof T> = {
  [P in Exclude<keyof T, K>]: T[P];
};

type Record<K extends string | number | symbol, T> = {
  [P in K]: T;
};

type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};
```

All built-in utility types are implemented with mapped types.

## Real-World Example: Type-Safe Form State

```ts
type FormField<T> = {
  value: T;
  error?: string;
  touched: boolean;
};

type FormState<T> = {
  [K in keyof T]: FormField<T[K]>;
};

type User = {
  name: string;
  email: string;
  age: number;
};

type UserFormState = FormState<User>;

const form: UserFormState = {
  name: { value: '', error: undefined, touched: false },
  email: { value: '', error: undefined, touched: false },
  age: { value: 0, error: undefined, touched: false },
};

type FormValidators<T> = {
  [K in keyof T]?: (value: T[K]) => string | undefined;
};

const validators: FormValidators<User> = {
  name: (value) => (value.length < 2 ? 'Name too short' : undefined),
  email: (value) => (value.includes('@') ? undefined : 'Invalid email'),
  age: (value) => (value >= 18 ? undefined : 'Must be 18+'),
};
```

Mapped types enable type-safe form handling.

## Key Remapping with Union Types

Distribute key remapping over unions:

```ts
type Action =
  | { type: 'increment'; by: number }
  | { type: 'decrement'; by: number }
  | { type: 'reset' };

type ActionCreators = {
  [A in Action as A['type']]: (
    ...args: A extends { by: number } ? [by: number] : []
  ) => A;
};

const actions: ActionCreators = {
  increment: (by) => ({ type: 'increment', by }),
  decrement: (by) => ({ type: 'decrement', by }),
  reset: () => ({ type: 'reset' }),
};
```

Key remapping works with discriminated unions.

## Combining Multiple Mapped Types

Chain mapped types for complex transformations:

```ts
type ReadonlyPartial<T> = Readonly<Partial<T>>;

type RequiredNonNullable<T> = {
  [K in keyof T]-?: NonNullable<T[K]>;
};

type DeepReadonlyPartial<T> = {
  readonly [K in keyof T]?: T[K] extends object
    ? DeepReadonlyPartial<T[K]>
    : T[K];
};

type Mutable<T> = {
  -readonly [K in keyof T]: T[K];
};

type MutableRequired<T> = Mutable<Required<T>>;
```

Compose utility types to express complex requirements.
