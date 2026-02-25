---
title: Design for Testability
description: Deep modules, interface-first design, pure functions, and separating computation from I/O for testable architecture
tags:
  [
    deep-modules,
    interface-design,
    pure-functions,
    testability,
    separation-of-concerns,
    computation-vs-io,
    architecture,
  ]
---

# Design for Testability

## Deep Modules

From John Ousterhout's "A Philosophy of Software Design": a deep module has a small interface relative to the functionality it provides. Deep modules are easier to test because fewer tests cover more behavior.

### Shallow Module (Hard to Test)

```ts
class UserValidator {
  validateEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  validateName(name: string): boolean {
    return name.length >= 2 && name.length <= 50;
  }

  validateAge(age: number): boolean {
    return age >= 0 && age <= 150;
  }

  validateAddress(address: Address): boolean {
    return !!address.street && !!address.city && !!address.zip;
  }
}
```

Four public methods, each trivial. Every internal change forces a test update. The class is just a bag of functions with no cohesion.

### Deep Module (Easy to Test)

```ts
type ValidationResult = { valid: true } | { valid: false; errors: string[] };

function validateUser(input: unknown): ValidationResult {
  const errors: string[] = [];

  if (!isValidEmail(input.email)) errors.push('Invalid email');
  if (!isValidName(input.name)) errors.push('Name must be 2-50 characters');
  if (!isValidAge(input.age)) errors.push('Age must be 0-150');
  if (!isValidAddress(input.address)) errors.push('Address is incomplete');

  return errors.length === 0 ? { valid: true } : { valid: false, errors };
}
```

One public function, one test surface. Internal validation helpers are private — they can change freely. Tests cover the behavior: valid input passes, invalid input returns specific errors.

```ts
describe('validateUser', () => {
  it('accepts valid user input', () => {
    const result = validateUser({
      email: 'alice@example.com',
      name: 'Alice',
      age: 30,
      address: { street: '123 Main', city: 'Springfield', zip: '62701' },
    });

    expect(result).toEqual({ valid: true });
  });

  it('collects all validation errors', () => {
    const result = validateUser({
      email: 'bad',
      name: 'A',
      age: -1,
      address: { street: '', city: '', zip: '' },
    });

    expect(result.valid).toBe(false);
    expect(result.errors).toHaveLength(4);
  });
});
```

## Interface-First Design

The first test is an API design decision. Writing the test before the implementation forces you to design the interface from the caller's perspective.

### The Process

```text
1. Write the test call:    const result = processOrder(items, discount);
2. Define the interface:   What does processOrder accept? What does it return?
3. Implement to pass:      Build the internals to satisfy the contract
```

If the test is awkward to write, the interface is awkward to use. Fix the interface before implementing.

### Awkward Test = Awkward Interface

```ts
// Awkward: caller must know internal steps
const processor = new OrderProcessor();
processor.setItems(items);
processor.setDiscount(discount);
processor.validate();
processor.calculateTotals();
const result = processor.getResult();
```

The test reveals that the caller must call five methods in the right order. The interface leaks implementation steps.

### Clean Test = Clean Interface

```ts
// Clean: one call, clear contract
const result = processOrder(items, discount);

expect(result.total).toBe(180);
expect(result.discount).toBe(20);
expect(result.items).toHaveLength(3);
```

The test reads like a specification. One function call, clear inputs, clear outputs.

## Return Values Over Side Effects

Pure functions that return values are trivially testable. Functions that mutate state or trigger side effects require setup, teardown, and assertions on external state.

### Hard to Test: Side Effects

```ts
let notifications: string[] = [];

function processRefund(order: Order) {
  order.status = 'refunded';
  order.refundedAt = new Date();
  notifications.push(`Refund processed for order ${order.id}`);
  db.orders.update(order);
  emailService.send(order.customerEmail, 'Your refund has been processed');
}
```

Testing requires mocking `db`, `emailService`, capturing `notifications`, and checking mutation of the `order` object. Five things to verify for one function.

### Easy to Test: Return Value

```ts
type RefundResult = {
  updatedOrder: Order;
  notification: string;
  email: { to: string; body: string };
};

function processRefund(order: Order, now: Date = new Date()): RefundResult {
  return {
    updatedOrder: { ...order, status: 'refunded', refundedAt: now },
    notification: `Refund processed for order ${order.id}`,
    email: {
      to: order.customerEmail,
      body: 'Your refund has been processed',
    },
  };
}
```

```ts
it('produces refund result with updated status and notification', () => {
  const order = { id: '123', status: 'paid', customerEmail: 'a@b.com' };
  const now = new Date('2025-01-15');

  const result = processRefund(order, now);

  expect(result.updatedOrder.status).toBe('refunded');
  expect(result.updatedOrder.refundedAt).toEqual(now);
  expect(result.notification).toContain('123');
  expect(result.email.to).toBe('a@b.com');
});
```

No mocks, no setup, no teardown. The caller decides what to do with the result — persist it, send the email, or both.

## Separate Computation from I/O

Structure applications as a pure computational core with thin I/O adapters at the boundaries.

```text
┌─────────────────────────────────┐
│         I/O Boundary            │  ← Thin adapter: HTTP, DB, filesystem
├─────────────────────────────────┤
│       Pure Computation          │  ← Rich logic: validation, transforms,
│                                 │     business rules, calculations
├─────────────────────────────────┤
│         I/O Boundary            │  ← Thin adapter: persist, notify, respond
└─────────────────────────────────┘
```

### Example: Order Processing

```ts
// Pure computation — testable without mocks
function buildInvoice(order: Order, taxRate: number): Invoice {
  const subtotal = order.items.reduce(
    (sum, item) => sum + item.price * item.qty,
    0,
  );
  const tax = Math.round(subtotal * taxRate);
  return {
    orderId: order.id,
    subtotal,
    tax,
    total: subtotal + tax,
    lineItems: order.items.map((item) => ({
      description: item.name,
      amount: item.price * item.qty,
    })),
  };
}

// I/O adapter — thin, delegates to pure core
async function handleOrderRequest(
  req: Request,
  db: Database,
  taxService: TaxService,
): Promise<Response> {
  const order = await db.orders.findById(req.params.id);
  const taxRate = await taxService.getRateForRegion(order.region);
  const invoice = buildInvoice(order, taxRate);
  await db.invoices.save(invoice);
  return Response.json(invoice);
}
```

`buildInvoice` is pure — test it exhaustively with simple input/output assertions. `handleOrderRequest` is a thin adapter — integration test it once to verify the wiring.

### Applying the Pattern

| Layer            | Characteristics                | Testing strategy                 |
| ---------------- | ------------------------------ | -------------------------------- |
| I/O adapters     | Thin, no business logic        | Integration tests, few cases     |
| Pure computation | No dependencies, deterministic | Unit tests, many cases           |
| Orchestration    | Wires adapters to computation  | Integration tests, happy + error |

The majority of tests target the pure computation layer. Adapters are tested sparingly — they're too simple to contain bugs worth catching.

### Design Heuristic

When a function is hard to test, ask: "Can I split the pure computation from the I/O?" Almost always, yes. Extract the computation, return data, and let the caller handle I/O.
