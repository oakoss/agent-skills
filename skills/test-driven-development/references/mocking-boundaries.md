---
title: Mocking Boundaries
description: Boundary rule for mocking, test double taxonomy, dependency injection patterns, and mocking anti-patterns
tags:
  [
    mocking,
    test-doubles,
    stubs,
    spies,
    fakes,
    dependency-injection,
    boundaries,
    I/O,
  ]
---

# Mocking Boundaries

## The Boundary Rule

Mock at I/O boundaries. Never mock internal collaborators.

| Mock (external boundary)  | Do not mock (internal collaborator)    |
| ------------------------- | -------------------------------------- |
| HTTP clients / `fetch`    | Your own service classes               |
| Database connections      | Utility functions in the same codebase |
| Filesystem operations     | Domain logic modules                   |
| System clock / `Date.now` | Data transformation helpers            |
| Email/SMS services        | Validation functions                   |
| Third-party API SDKs      | State management stores                |
| Random number generators  | Event emitters you own                 |

Internal collaborators are implementation details. Mocking them couples tests to structure, not behavior.

## Test Double Taxonomy

| Double | What It Does                          | When to Use                                               |
| ------ | ------------------------------------- | --------------------------------------------------------- |
| Stub   | Returns canned data, no assertions    | Replace a dependency to control inputs                    |
| Spy    | Records calls, delegates to real impl | Verify a side effect happened (email sent, event emitted) |
| Fake   | Working implementation, simplified    | In-memory database, local filesystem, fake clock          |
| Mock   | Pre-programmed expectations           | When call order and exact arguments matter (rare)         |

Prefer stubs and fakes. They make tests less brittle than mocks with strict call expectations.

### Stub Example

```ts
import { describe, it, expect, vi } from 'vitest';
import { PricingService } from './pricing-service';
import { type ExchangeRateClient } from './exchange-rate-client';

describe('PricingService.convertPrice', () => {
  it('converts USD to EUR using current rate', () => {
    const rateClient: ExchangeRateClient = {
      getRate: vi.fn().mockResolvedValue(0.85),
    };
    const service = new PricingService(rateClient);

    const result = await service.convertPrice(100, 'USD', 'EUR');

    expect(result).toBe(85);
  });
});
```

The stub controls the external boundary (exchange rate API) without asserting how it was called.

### Fake Example

```ts
import { describe, it, expect } from 'vitest';
import { UserRepository } from './user-repository';

class InMemoryUserStore {
  private users = new Map<string, User>();

  async save(user: User) {
    this.users.set(user.id, user);
  }

  async findById(id: string) {
    return this.users.get(id) ?? null;
  }
}

describe('UserRepository', () => {
  it('retrieves a saved user', async () => {
    const store = new InMemoryUserStore();
    const repo = new UserRepository(store);

    await repo.create({ id: '1', name: 'Alice' });
    const found = await repo.findById('1');

    expect(found).toEqual({ id: '1', name: 'Alice' });
  });
});
```

The fake provides a working in-memory implementation. Tests run fast and verify real behavior without a database.

## Dependency Injection for Testability

Accept dependencies as parameters instead of importing them directly. This makes boundaries mockable without patching modules.

### Bad: Direct Import

```ts
import { fetch } from 'undici';

export async function getUser(id: string) {
  const res = await fetch(`https://api.example.com/users/${id}`);
  return res.json();
}
```

Testing requires patching the `fetch` module — fragile and couples tests to import structure.

### Good: Parameter Injection

```ts
type HttpClient = {
  get: (url: string) => Promise<Response>;
};

export async function getUser(id: string, client: HttpClient) {
  const res = await client.get(`https://api.example.com/users/${id}`);
  return res.json();
}
```

Tests inject a stub client. Production code injects the real client. No module patching needed.

### Good: Default Parameter

```ts
type HttpClient = {
  get: (url: string) => Promise<Response>;
};

export async function getUser(
  id: string,
  client: HttpClient = defaultHttpClient,
) {
  const res = await client.get(`https://api.example.com/users/${id}`);
  return res.json();
}
```

Default parameter keeps the call site clean while remaining testable.

## Anti-Patterns

### Mocking the Module Under Test

```ts
// WRONG: mocking internal methods of the thing you're testing
const service = new OrderService();
vi.spyOn(service, 'calculateTotal').mockReturnValue(100);
service.placeOrder(items);
expect(service.calculateTotal).toHaveBeenCalled();
```

This tests that your mock was called, not that the code works. Test through the public interface instead.

### Mock Chains

```ts
// WRONG: deep mock chain reveals coupling
const mockDb = {
  connection: {
    manager: {
      query: vi.fn().mockResolvedValue([{ id: 1 }]),
    },
  },
};
```

If a test requires reaching three levels deep into an object, the production code has the same coupling problem. Wrap the database behind a simple interface.

### Asserting Call Counts

```ts
// WRONG: brittle — breaks if implementation caches or batches
expect(fetchSpy).toHaveBeenCalledTimes(3);
```

Assert on the outcome, not how many times an internal dependency was invoked. The implementation may batch, cache, or deduplicate — that's its prerogative.

### Over-Mocking: Everything Is a Mock

```ts
// WRONG: mocking your own utility
vi.mock('./utils/format-currency');
```

`formatCurrency` is a pure function you own. Use the real implementation. The test should verify that the formatted result appears in the output, not that a formatter was called.
