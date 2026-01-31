---
title: Page Object Model
description: Page Object Model architecture with Playwright, base page classes, fixture integration, component objects, and single responsibility patterns
tags:
  [page-object-model, pom, fixtures, base-page, component-objects, architecture]
---

# Page Object Model

## Why POM

The Page Object Model encapsulates page-specific locators and actions into classes, keeping test files focused on user behavior rather than DOM structure. When UI changes, update one POM class instead of every test.

## Basic POM Structure

```ts
import { type Locator, type Page, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email address');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/auth/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }
}
```

## Using POMs in Tests

```ts
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login-page';

test('successful login redirects to dashboard', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password123');

  await expect(page).toHaveURL('/dashboard');
});

test('invalid credentials show error', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'wrong');

  await loginPage.expectError('Invalid credentials');
});
```

## Integrating POMs with Fixtures

Reduce boilerplate by extending Playwright fixtures to provide POMs automatically:

```ts
import { test as base } from '@playwright/test';
import { LoginPage } from './pages/login-page';
import { DashboardPage } from './pages/dashboard-page';

type Fixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
};

export const test = base.extend<Fixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
});

export { expect } from '@playwright/test';
```

Then use in tests:

```ts
import { test, expect } from './fixtures';

test('dashboard shows user name', async ({ loginPage, dashboardPage }) => {
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password123');

  await expect(dashboardPage.welcomeMessage).toContainText('Welcome');
});
```

## Base Page Class

Extract common functionality into a base class:

```ts
import { type Locator, type Page, expect } from '@playwright/test';

export abstract class BasePage {
  readonly page: Page;
  readonly heading: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { level: 1 });
  }

  async expectHeading(text: string) {
    await expect(this.heading).toHaveText(text);
  }

  async expectURL(path: string) {
    await expect(this.page).toHaveURL(path);
  }
}
```

Extend for specific pages:

```ts
import { type Locator, type Page } from '@playwright/test';
import { BasePage } from './base-page';

export class SettingsPage extends BasePage {
  readonly saveButton: Locator;
  readonly nameInput: Locator;

  constructor(page: Page) {
    super(page);
    this.saveButton = page.getByRole('button', { name: 'Save changes' });
    this.nameInput = page.getByLabel('Display name');
  }

  async goto() {
    await this.page.goto('/settings');
  }

  async updateName(name: string) {
    await this.nameInput.fill(name);
    await this.saveButton.click();
  }
}
```

## Component Objects

For reusable UI components that appear on multiple pages, create component objects:

```ts
import { type Locator, type Page, expect } from '@playwright/test';

export class NavigationBar {
  readonly container: Locator;
  readonly searchInput: Locator;
  readonly profileMenu: Locator;

  constructor(page: Page) {
    this.container = page.getByRole('navigation');
    this.searchInput = this.container.getByRole('searchbox');
    this.profileMenu = this.container.getByRole('button', { name: 'Profile' });
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
  }

  async openProfile() {
    await this.profileMenu.click();
  }
}
```

Compose into page objects:

```ts
import { type Locator, type Page } from '@playwright/test';
import { BasePage } from './base-page';
import { NavigationBar } from './components/navigation-bar';

export class DashboardPage extends BasePage {
  readonly nav: NavigationBar;
  readonly welcomeMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.nav = new NavigationBar(page);
    this.welcomeMessage = page.getByRole('heading', { level: 2 });
  }
}
```

## Project Structure

```sh
tests/
├── fixtures.ts           # Custom fixtures with POMs
├── pages/                # Page objects
│   ├── base-page.ts
│   ├── login-page.ts
│   ├── dashboard-page.ts
│   └── settings-page.ts
├── components/           # Reusable component objects
│   └── navigation-bar.ts
├── auth.setup.ts         # Authentication setup
└── specs/                # Test files
    ├── login.spec.ts
    ├── dashboard.spec.ts
    └── settings.spec.ts
```

## POM Guidelines

- **Single responsibility**: One POM class per page or distinct section
- **No assertions in action methods**: Keep assertions in dedicated `expect*` methods or in test files
- **No state between tests**: POMs receive a fresh `page` instance per test
- **Use role-based locators**: Define locators with `getByRole`, `getByLabel`, `getByText` in the constructor
- **Keep methods user-centric**: Name methods after user actions (`login`, `submitForm`, `openSettings`) not implementation details (`clickButton`, `fillInput`)
- **Return types for navigation**: Methods that navigate to a new page can return the target POM
