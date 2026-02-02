---
paths:
  - 'skills/*test*/references/**'
  - 'skills/playwright/references/**'
  - 'skills/quality-auditor/references/**'
  - 'skills/**/references/*test*'
  - 'skills/**/references/*mock*'
  - 'skills/**/references/*assertion*'
  - 'skills/**/references/*spec*'
---

# Testing Rules

## Structure

- Use BDD-style comments: `#given`, `#when`, `#then`
- One logical assertion per test
- Descriptive test names that explain the scenario

## Mocking

- Mock external dependencies (APIs, databases, server functions)
- Don't mock the unit under test
- Reset mocks between tests with `vi.clearAllMocks()` in `beforeEach`

## Coverage

- Test happy path AND error cases
- Test edge cases (empty, null, boundary values)
- Test async behavior (loading, success, error states)

## Example

```ts
describe('UserService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getUser', () => {
    it('returns user when found', async () => {
      // #given
      const mockUser = { id: '1', name: 'Test' };
      vi.mocked(db.user.findById).mockResolvedValue(mockUser);

      // #when
      const result = await userService.getUser('1');

      // #then
      expect(result).toEqual(mockUser);
    });

    it('throws NotFoundError when user does not exist', async () => {
      // #given
      vi.mocked(db.user.findById).mockResolvedValue(null);

      // #when & #then
      await expect(userService.getUser('999')).rejects.toThrow(NotFoundError);
    });
  });
});
```

## Test Naming

Use `it('does X when Y')` format:

| Bad                        | Good                                      |
| -------------------------- | ----------------------------------------- |
| `it('test user')`          | `it('returns user when found')`           |
| `it('error case')`         | `it('throws NotFoundError when null')`    |
| `it('should work')`        | `it('submits form with valid data')`      |
| `it('handles edge cases')` | `it('returns empty array when no items')` |

## Testing React Components

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('Button', () => {
  it('calls onPress when clicked', async () => {
    // #given
    const handlePress = vi.fn();
    render(<Button onPress={handlePress}>Click me</Button>);

    // #when
    await userEvent.click(screen.getByRole('button'));

    // #then
    expect(handlePress).toHaveBeenCalledOnce();
  });
});
```

## Testing Server Functions

```ts
describe('createPost', () => {
  it('creates post when authenticated', async () => {
    // #given
    vi.mocked(auth.api.getSession).mockResolvedValue({ user: { id: '1' } });
    vi.mocked(db.insert).mockResolvedValue([{ id: 'post-1' }]);

    // #when
    const result = await createPost({ data: { title: 'Test' } });

    // #then
    expect(result).toEqual({ id: 'post-1' });
  });

  it('returns AUTH_REQUIRED when not authenticated', async () => {
    // #given
    vi.mocked(auth.api.getSession).mockResolvedValue(null);

    // #when
    const result = await createPost({ data: { title: 'Test' } });

    // #then
    expect(result).toEqual({
      error: expect.any(String),
      code: 'AUTH_REQUIRED',
    });
  });
});
```
