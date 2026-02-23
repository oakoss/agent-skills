---
title: Form Actions
description: SvelteKit form actions, progressive enhancement with use:enhance, validation, and error handling
tags: [form, actions, enhance, validation, progressive, fail, superforms]
---

# Form Actions

## Basic Form Actions

Form actions handle POST requests in `+page.server.ts`. They work without JavaScript, providing progressive enhancement.

```ts
// src/routes/login/+page.server.ts
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions = {
  default: async ({ request, cookies }) => {
    const data = await request.formData();
    const email = data.get('email') as string;
    const password = data.get('password') as string;

    if (!email || !password) {
      return fail(400, { email, missing: true });
    }

    const user = await authenticate(email, password);
    if (!user) {
      return fail(401, { email, incorrect: true });
    }

    cookies.set('session', user.token, { path: '/', httpOnly: true });
    redirect(303, '/dashboard');
  },
} satisfies Actions;
```

```svelte
<!-- src/routes/login/+page.svelte -->
<script lang="ts">
  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();
</script>

<form method="POST">
  <label>
    Email
    <input name="email" type="email" value={form?.email ?? ''} />
  </label>

  <label>
    Password
    <input name="password" type="password" />
  </label>

  {#if form?.missing}
    <p class="error">All fields are required</p>
  {/if}

  {#if form?.incorrect}
    <p class="error">Invalid credentials</p>
  {/if}

  <button>Log in</button>
</form>
```

## Named Actions

Define multiple actions on a single page.

```ts
// src/routes/todos/+page.server.ts
import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions = {
  create: async ({ request, locals }) => {
    const data = await request.formData();
    const text = data.get('text') as string;

    if (!text?.trim()) {
      return fail(400, { text, error: 'Text is required' });
    }

    await locals.db.todo.create({ data: { text, userId: locals.user.id } });
    return { success: true };
  },

  delete: async ({ request, locals }) => {
    const data = await request.formData();
    const id = data.get('id') as string;

    await locals.db.todo.delete({ where: { id, userId: locals.user.id } });
    return { success: true };
  },

  toggle: async ({ request, locals }) => {
    const data = await request.formData();
    const id = data.get('id') as string;

    const todo = await locals.db.todo.findUnique({ where: { id } });
    if (todo) {
      await locals.db.todo.update({
        where: { id },
        data: { done: !todo.done },
      });
    }
  },
} satisfies Actions;
```

```svelte
<!-- src/routes/todos/+page.svelte -->
<script lang="ts">
  import type { PageData, ActionData } from './$types';

  let { data, form }: { data: PageData; form: ActionData } = $props();
</script>

<form method="POST" action="?/create">
  <input name="text" value={form?.text ?? ''} />
  {#if form?.error}
    <p class="error">{form.error}</p>
  {/if}
  <button>Add</button>
</form>

{#each data.todos as todo (todo.id)}
  <div>
    <form method="POST" action="?/toggle" style="display:inline">
      <input type="hidden" name="id" value={todo.id} />
      <button>{todo.done ? 'Undo' : 'Done'}</button>
    </form>

    <span class:done={todo.done}>{todo.text}</span>

    <form method="POST" action="?/delete" style="display:inline">
      <input type="hidden" name="id" value={todo.id} />
      <button>Delete</button>
    </form>
  </div>
{/each}
```

## Progressive Enhancement with use:enhance

The `enhance` action upgrades forms to use fetch instead of full page reloads while maintaining the same server-side logic.

```svelte
<script>
  import { enhance } from '$app/forms';
</script>

<!-- Basic: auto-invalidates load functions after submission -->
<form method="POST" action="?/create" use:enhance>
  <input name="text" />
  <button>Add</button>
</form>
```

### Custom enhance behavior

```svelte
<script>
  import { enhance } from '$app/forms';

  let submitting = $state(false);
</script>

<form
  method="POST"
  action="?/create"
  use:enhance={() => {
    submitting = true;

    return async ({ result, update }) => {
      submitting = false;

      if (result.type === 'success') {
        showToast('Created successfully');
      }

      await update();
    };
  }}
>
  <input name="text" />
  <button disabled={submitting}>
    {submitting ? 'Saving...' : 'Add'}
  </button>
</form>
```

### Cancelling default behavior

```svelte
<form
  method="POST"
  use:enhance={() => {
    return async ({ result }) => {
      if (result.type === 'redirect') {
        goto(result.location);
      }
      // Omitting update() prevents auto-invalidation
    };
  }}
>
```

## Validation Patterns

### Server-side validation with typed errors

```ts
// src/routes/register/+page.server.ts
import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();
    const email = data.get('email') as string;
    const password = data.get('password') as string;

    const errors: Record<string, string> = {};

    if (!email?.includes('@')) {
      errors.email = 'Invalid email address';
    }

    if (!password || password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }

    if (Object.keys(errors).length > 0) {
      return fail(400, { errors, email });
    }

    await createUser(email, password);
    return { success: true };
  },
} satisfies Actions;
```

### File uploads

```svelte
<form method="POST" enctype="multipart/form-data" use:enhance>
  <input type="file" name="avatar" accept="image/*" />
  <button>Upload</button>
</form>
```

```ts
// +page.server.ts
export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();
    const file = data.get('avatar') as File;

    if (file.size > 5 * 1024 * 1024) {
      return fail(400, { error: 'File too large (max 5MB)' });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    await saveFile(buffer, file.name);
    return { success: true };
  },
} satisfies Actions;
```
