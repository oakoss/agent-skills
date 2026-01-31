---
title: Conditional Types
description: Type-level conditionals, distributive types, infer keyword, and type-level logic
tags: [conditional-types, extends, infer, distributive, type-level-logic]
---

# Conditional Types

Conditional types enable type-level if-else logic using the `extends` keyword.

## Basic Conditional Types

Use `T extends U ? X : Y` for type-level conditionals:

```ts
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;
type B = IsString<number>;

type NonNullable<T> = T extends null | undefined ? never : T;

type C = NonNullable<string | null>;

type Flatten<T> = T extends unknown[] ? T[0] : T;

type D = Flatten<string[]>;
type E = Flatten<number>;
```

Conditional types are evaluated when the type parameter is known.

## Distributive Conditional Types

Conditional types distribute over unions:

```ts
type ToArray<T> = T extends unknown ? T[] : never;

type F = ToArray<string | number>;

type Filter<T, U> = T extends U ? T : never;

type G = Filter<'a' | 'b' | 'c' | 'd', 'a' | 'c'>;

type NonNullable<T> = T extends null | undefined ? never : T;

type H = NonNullable<string | null | number | undefined>;
```

When `T` is a union, the conditional type is applied to each member separately.

## Preventing Distribution

Use square brackets to prevent distribution:

```ts
type ToArray<T> = [T] extends [unknown] ? T[] : never;

type I = ToArray<string | number>;

type IsUnion<T> = [T] extends [T] ? false : true;

type J = IsUnion<string>;
type K = IsUnion<string | number>;
```

Wrapping types in tuples disables distributive behavior.

## infer Keyword

Extract types from other types with `infer`:

```ts
type ReturnType<T> = T extends (...args: unknown[]) => infer R ? R : never;

type L = ReturnType<() => string>;

type Parameters<T> = T extends (...args: infer P) => unknown ? P : never;

type M = Parameters<(a: string, b: number) => void>;

type Unpromisify<T> = T extends Promise<infer U> ? U : T;

type N = Unpromisify<Promise<string>>;
type O = Unpromisify<number>;
```

`infer R` declares a type variable within the conditional type.

## Multiple infer

Use multiple `infer` declarations:

```ts
type FirstArg<T> = T extends (first: infer F, ...rest: unknown[]) => unknown
  ? F
  : never;

type P = FirstArg<(a: string, b: number) => void>;

type SecondArg<T> = T extends (
  first: unknown,
  second: infer S,
  ...rest: unknown[]
) => unknown
  ? S
  : never;

type Q = SecondArg<(a: string, b: number, c: boolean) => void>;

type Awaited<T> =
  T extends Promise<infer U>
    ? U extends Promise<infer V>
      ? Awaited<V>
      : U
    : T;

type R = Awaited<Promise<Promise<string>>>;
```

Multiple `infer` declarations enable complex type extraction.

## Conditional Chains

Chain conditional types for complex logic:

```ts
type TypeName<T> = T extends string
  ? 'string'
  : T extends number
    ? 'number'
    : T extends boolean
      ? 'boolean'
      : T extends undefined
        ? 'undefined'
        : T extends Function
          ? 'function'
          : 'object';

type S = TypeName<string>;
type T = TypeName<() => void>;

type IsArray<T> = T extends unknown[]
  ? true
  : T extends readonly unknown[]
    ? true
    : false;

type U = IsArray<string[]>;
type V = IsArray<readonly number[]>;
```

Conditional chains behave like nested if-else statements.

## Type-Level Utilities

Build reusable type utilities:

```ts
type GetProperty<T, K> = K extends keyof T ? T[K] : never;

type W = GetProperty<{ a: string; b: number }, 'a'>;

type RequiredKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? never : K;
}[keyof T];

type X = RequiredKeys<{ a: string; b?: number }>;

type OptionalKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? K : never;
}[keyof T];

type Y = OptionalKeys<{ a: string; b?: number }>;
```

Combine conditional types with mapped types for powerful transformations.

## Function Overload Resolution

Extract specific overload signatures:

```ts
type OverloadedFunction = {
  (a: string): string;
  (a: number): number;
  (a: boolean): boolean;
};

type GetOverload<T, Args extends unknown[]> = T extends {
  (...args: infer P): infer R;
}
  ? P extends Args
    ? R
    : never
  : never;

type Z = GetOverload<OverloadedFunction, [string]>;
```

Conditional types can narrow overloaded function signatures.

## Recursive Conditional Types

Recursively unwrap nested types:

```ts
type DeepAwaited<T> = T extends Promise<infer U> ? DeepAwaited<U> : T;

type AA = DeepAwaited<Promise<Promise<Promise<string>>>>;

type DeepReadonly<T> = T extends object
  ? {
      readonly [K in keyof T]: DeepReadonly<T[K]>;
    }
  : T;

type AB = DeepReadonly<{ a: { b: { c: string } } }>;

type DeepPartial<T> = T extends object
  ? {
      [K in keyof T]?: DeepPartial<T[K]>;
    }
  : T;

type AC = DeepPartial<{ a: { b: { c: string } } }>;
```

Recursive conditional types handle arbitrarily nested structures.

## Type-Level Equality

Check if two types are equal:

```ts
type Equals<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends <T>() => T extends Y ? 1 : 2
    ? true
    : false;

type AD = Equals<string, string>;
type AE = Equals<string, number>;

type IsAny<T> = 0 extends 1 & T ? true : false;

type AF = IsAny<any>;
type AG = IsAny<unknown>;
```

Type-level equality is useful for testing and advanced type transformations.

## Conditional Type Constraints

Constrain conditional types with `extends`:

```ts
type ExtractArrayElement<T> = T extends (infer E)[] ? E : never;

type AH = ExtractArrayElement<string[]>;

type UnwrapPromise<T extends Promise<unknown>> =
  T extends Promise<infer U> ? U : never;

type AI = UnwrapPromise<Promise<string>>;

type GetKeys<T extends object> = keyof T;

type AJ = GetKeys<{ a: string; b: number }>;
```

Constraints ensure conditional types are only applied to valid inputs.

## Real-World Example: Type-Safe Event Emitter

```ts
type EventMap = {
  click: { x: number; y: number };
  scroll: { top: number; left: number };
  resize: { width: number; height: number };
};

type EventHandler<T> = (payload: T) => void;

class TypedEmitter<Events extends Record<string, unknown>> {
  private handlers = new Map<keyof Events, Set<EventHandler<unknown>>>();

  on<K extends keyof Events>(event: K, handler: EventHandler<Events[K]>) {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler as EventHandler<unknown>);
  }

  emit<K extends keyof Events>(event: K, payload: Events[K]) {
    const handlers = this.handlers.get(event);
    if (!handlers) return;
    for (const handler of handlers) {
      handler(payload);
    }
  }
}

const emitter = new TypedEmitter<EventMap>();
emitter.on('click', ({ x, y }) => console.log(x, y));
emitter.emit('click', { x: 10, y: 20 });
```

Conditional types enable fully type-safe event systems.
