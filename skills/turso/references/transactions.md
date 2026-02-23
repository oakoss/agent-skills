---
title: Transactions
description: Batch operations, interactive transactions, transaction modes, and atomic multi-statement execution
tags: [batch, transaction, commit, rollback, write, read, deferred, atomic]
---

# Transactions

## Batch Operations

Batch executes multiple SQL statements atomically in a single round-trip:

```ts
await client.batch(
  [
    'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT)',
    "INSERT INTO users VALUES (1, 'first@example.com')",
    "INSERT INTO users VALUES (2, 'second@example.com')",
  ],
  'write',
);
```

### Parameterized Batch

```ts
const results = await client.batch(
  [
    {
      sql: 'INSERT INTO users (email) VALUES (?)',
      args: ['alice@example.com'],
    },
    {
      sql: 'INSERT INTO users (email) VALUES (?)',
      args: ['bob@example.com'],
    },
    {
      sql: 'SELECT * FROM users WHERE email LIKE ?',
      args: ['%@example.com'],
    },
  ],
  'write',
);

console.log(results[0].lastInsertRowid);
console.log(results[2].rows);
```

### Named Parameters in Batch

```ts
await client.batch(
  [
    {
      sql: 'UPDATE users SET email = $new WHERE email = $old',
      args: { old: 'alice@example.com', new: 'alice.smith@example.com' },
    },
    {
      sql: 'DELETE FROM users WHERE email = $email',
      args: { email: 'bob@example.com' },
    },
  ],
  'write',
);
```

### Read-Only Batch

```ts
const [countResult, usersResult] = await client.batch(
  [
    'SELECT COUNT(*) as total FROM users',
    'SELECT * FROM users ORDER BY id DESC LIMIT 10',
  ],
  'read',
);
```

## Transaction Modes

| Mode         | Behavior                                              |
| ------------ | ----------------------------------------------------- |
| `'write'`    | Acquires write lock immediately                       |
| `'read'`     | Read-only, concurrent with other reads                |
| `'deferred'` | Starts as read, upgrades to write on first write stmt |

## Interactive Transactions

For multi-step operations with application logic between statements:

```ts
const transaction = await client.transaction('write');

try {
  await transaction.execute({
    sql: 'UPDATE accounts SET balance = balance - ? WHERE name = ?',
    args: [100, 'Alice'],
  });

  const balance = await transaction.execute({
    sql: 'SELECT balance FROM accounts WHERE name = ?',
    args: ['Alice'],
  });

  if ((balance.rows[0].balance as number) < 0) {
    throw new Error('Insufficient funds');
  }

  await transaction.execute({
    sql: 'UPDATE accounts SET balance = balance + ? WHERE name = ?',
    args: [100, 'Bob'],
  });

  await transaction.commit();
} catch (error) {
  await transaction.rollback();
  throw error;
} finally {
  transaction.close();
}
```

## Batch vs Interactive Transaction

| Feature                   | `batch()`               | `transaction()`          |
| ------------------------- | ----------------------- | ------------------------ |
| Round-trips               | Single                  | Multiple                 |
| Application logic between | No                      | Yes                      |
| Performance               | Better (one round-trip) | More flexible            |
| Error handling            | All-or-nothing          | Manual commit/rollback   |
| Use case                  | Known set of statements | Conditional logic needed |

Prefer `batch()` when all statements are known upfront. Use interactive transactions only when application logic must run between database operations.
