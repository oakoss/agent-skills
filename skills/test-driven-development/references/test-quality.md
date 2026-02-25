---
title: Test Quality
description: Good vs bad test patterns, what to test, behavior-oriented naming, triangulation, and refactoring signals
tags:
  [
    behavior-testing,
    test-naming,
    triangulation,
    refactoring,
    public-interface,
    test-structure,
    arrange-act-assert,
  ]
---

# Test Quality

## Good Tests vs Bad Tests

Good tests assert behavior through the public interface. Bad tests mirror implementation details and break on every refactor.

### Bad: Testing Implementation Details

```ts
import { describe, it, expect, vi } from 'vitest';
import { OrderService } from './order-service';

describe('OrderService', () => {
  it('calls validateItems and calculateTotal internally', () => {
    const service = new OrderService();
    const validateSpy = vi.spyOn(service as any, 'validateItems');
    const calculateSpy = vi.spyOn(service as any, 'calculateTotal');

    service.placeOrder([{ id: 'a', price: 10, qty: 2 }]);

    expect(validateSpy).toHaveBeenCalled();
    expect(calculateSpy).toHaveBeenCalledWith([{ id: 'a', price: 10, qty: 2 }]);
  });
});
```

This test breaks if internal method names change, even when behavior is identical. It tests HOW, not WHAT.

### Good: Testing Through the Public Interface

```ts
import { describe, it, expect } from 'vitest';
import { OrderService } from './order-service';

describe('OrderService.placeOrder', () => {
  it('returns order total for valid items', () => {
    const service = new OrderService();

    const result = service.placeOrder([{ id: 'a', price: 10, qty: 2 }]);

    expect(result.total).toBe(20);
    expect(result.status).toBe('confirmed');
  });

  it('rejects empty item list', () => {
    const service = new OrderService();

    expect(() => service.placeOrder([])).toThrow(
      'Order must contain at least one item',
    );
  });
});
```

Tests survive internal refactors. They describe what the caller experiences.

## What to Test

| Test                    | Example                                                         |
| ----------------------- | --------------------------------------------------------------- |
| Public return values    | `expect(calculate(10, 20)).toBe(30)`                            |
| Observable side effects | `expect(db.users.count()).toBe(1)` after `createUser()`         |
| Error paths             | `expect(() => withdraw(-1)).toThrow("Amount must be positive")` |
| Edge cases              | Empty inputs, boundary values, null/undefined                   |
| State transitions       | `expect(order.status).toBe("shipped")` after `ship(order)`      |

| Skip                         | Why                                        |
| ---------------------------- | ------------------------------------------ |
| Private methods              | Tested implicitly through public interface |
| Getters/setters              | Trivial; no logic to verify                |
| Framework internals          | Trust the framework; test your code        |
| Third-party library behavior | Not your responsibility                    |
| Type-level constraints       | TypeScript enforces these at compile time  |

## Test Naming

Name tests after behavior, not method names. A reader should understand what broke without reading the test body.

| Bad                      | Good                                        |
| ------------------------ | ------------------------------------------- |
| `test validateToken`     | `rejects expired tokens`                    |
| `test handleSubmit`      | `submits form and redirects to dashboard`   |
| `test processPayment`    | `charges the card and sends receipt email`  |
| `test calculateDiscount` | `applies 10% discount for orders over $100` |
| `test error handling`    | `returns 404 when user does not exist`      |

Use `describe` blocks to group by feature or scenario, not by class:

```ts
describe('checkout', () => {
  describe('with valid payment', () => {
    it('charges the card and creates the order', () => {
      // ...
    });

    it('sends confirmation email', () => {
      // ...
    });
  });

  describe('with expired card', () => {
    it('returns payment error without creating an order', () => {
      // ...
    });
  });
});
```

## Test Structure: Arrange-Act-Assert

Every test follows three phases. Blank lines separate them visually.

```ts
it('applies percentage discount to order total', () => {
  // Arrange
  const order = createOrder({ items: [{ price: 100, qty: 2 }] });
  const discount = { type: 'percentage' as const, value: 10 };

  // Act
  const result = applyDiscount(order, discount);

  // Assert
  expect(result.total).toBe(180);
  expect(result.savings).toBe(20);
});
```

Keep each phase short. If arrange needs 20 lines, extract a factory function. If act needs multiple steps, the interface may need simplification.

## Triangulation

When the simplest code to pass a test is a hardcoded value, add a second test case to force generalization.

```ts
// First test — could pass with `return 20`
it('calculates total for single item', () => {
  expect(calculateTotal([{ price: 10, qty: 2 }])).toBe(20);
});

// Second test — forces the real implementation
it('calculates total for multiple items', () => {
  expect(
    calculateTotal([
      { price: 10, qty: 2 },
      { price: 5, qty: 3 },
    ]),
  ).toBe(35);
});
```

Triangulation applies when the first GREEN pass is trivially hardcoded. If the first implementation is already general, skip the extra case.

## Refactoring Signals

Functions that are hard to test reveal design problems. The fix is not a more clever test — it is a better design.

| Signal                           | Design Problem                       | Fix                                              |
| -------------------------------- | ------------------------------------ | ------------------------------------------------ |
| Test needs 10+ lines of setup    | Function has too many dependencies   | Extract a focused function with fewer inputs     |
| Must mock internal collaborators | Tight coupling between modules       | Inject dependencies; split responsibilities      |
| Test breaks on unrelated changes | Function does too many things        | Single responsibility — split into smaller units |
| Cannot test without side effects | Logic mixed with I/O                 | Separate pure computation from I/O               |
| Asserting on call sequences      | Testing implementation, not behavior | Assert on outputs and observable state           |
| Need to access private state     | Public interface is incomplete       | Expose behavior through public methods           |
