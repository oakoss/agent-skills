---
title: Server Functions
description: createServerFn patterns including validation, authentication, request context, response headers, cookies, file uploads, streaming responses, and calling from components and TanStack Query
tags:
  [
    createServerFn,
    useServerFn,
    server-function,
    inputValidator,
    handler,
    POST,
    GET,
    zod,
    auth,
    request,
    headers,
    cookies,
    file-upload,
    streaming,
    query,
  ]
---

# Server Functions

## Basic Server Function with Validation

```ts
import { createServerFn } from '@tanstack/react-start';
import { z } from 'zod';

const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  published: z.boolean().default(false),
});

export const createPost = createServerFn({ method: 'POST' })
  .inputValidator(createPostSchema)
  .handler(async ({ data }) => {
    const post = await db.posts.create({ data });
    return post;
  });

export const getPost = createServerFn()
  .inputValidator(z.object({ id: z.string() }))
  .handler(async ({ data }) => {
    const post = await db.posts.findUnique({ where: { id: data.id } });
    if (!post) throw notFound();
    return post;
  });
```

## Use in Route Loaders

```ts
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => {
    return await getPost({ data: { id: params.postId } });
  },
});
```

## Authenticated Server Functions

```ts
const deletePost = createServerFn({ method: 'POST' })
  .inputValidator(z.object({ id: z.string() }))
  .handler(async ({ data, request }) => {
    const session = await getSession({ headers: request.headers });

    if (!session) {
      return { error: 'Authentication required', code: 'AUTH_REQUIRED' };
    }

    const post = await db.posts.findUnique({ where: { id: data.id } });

    if (post?.authorId !== session.user.id) {
      return { error: 'Not authorized', code: 'FORBIDDEN' };
    }

    await db.posts.delete({ where: { id: data.id } });
    return { success: true };
  });
```

## Request Context

```ts
const serverFn = createServerFn({ method: 'POST' }).handler(
  async ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    const url = new URL(request.url);
    const session = await getSession({ headers: request.headers });
  },
);
```

## Response Headers and Cookies

```ts
const setTheme = createServerFn({ method: 'POST' })
  .inputValidator(z.object({ theme: z.enum(['light', 'dark']) }))
  .handler(async ({ data }) => {
    return new Response(JSON.stringify({ success: true }), {
      headers: {
        'Set-Cookie': `theme=${data.theme}; Path=/; HttpOnly; SameSite=Lax`,
        'Content-Type': 'application/json',
      },
    });
  });

const getTheme = createServerFn().handler(async ({ request }) => {
  const cookies = request.headers.get('cookie') || '';
  const theme = cookies.match(/theme=(\w+)/)?.[1] || 'light';
  return { theme };
});
```

## Calling from Components

```tsx
function CreatePostForm() {
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);

    const result = await createPost({
      data: {
        title: formData.get('title') as string,
        content: formData.get('content') as string,
      },
    });

    if ('error' in result) {
      toast.error(result.error);
    } else {
      toast.success('Post created');
    }
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

## With TanStack Query

```tsx
import { queryOptions, useSuspenseQuery } from '@tanstack/react-query';

const postsQuery = queryOptions({
  queryKey: ['posts'],
  queryFn: () => getPosts(),
});

function PostList() {
  const { data: posts } = useSuspenseQuery(postsQuery);
}
```

## File Uploads

```ts
const uploadFile = createServerFn({ method: 'POST' }).handler(
  async ({ request }) => {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) throw new AppError('No file provided', 'VALIDATION_ERROR');

    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize)
      throw new AppError('File too large', 'VALIDATION_ERROR');

    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      throw new AppError('Invalid file type', 'VALIDATION_ERROR');
    }

    const buffer = await file.arrayBuffer();
    const filename = `${Date.now()}-${file.name}`;
    await writeFile(`./uploads/${filename}`, Buffer.from(buffer));

    return { filename, size: file.size };
  },
);
```

## Streaming Responses

```ts
const streamData = createServerFn().handler(async () => {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        controller.enqueue(encoder.encode(`data: ${i}\n\n`));
        await new Promise((r) => setTimeout(r, 100));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  });
});
```

## useServerFn Hook

Wraps a server function for use in components with pending state tracking:

```tsx
import { useServerFn } from '@tanstack/react-start';

function DeleteButton({ postId }: { postId: string }) {
  const deletePostFn = useServerFn(deletePost);

  const handleDelete = async () => {
    const result = await deletePostFn({ data: { id: postId } });
    if ('error' in result) {
      toast.error(result.error);
    }
  };

  return <button onClick={handleDelete}>Delete</button>;
}
```

Use with TanStack Query mutations for optimistic updates and cache invalidation:

```tsx
import { useServerFn } from '@tanstack/react-start';
import { useMutation, useQueryClient } from '@tanstack/react-query';

function CreatePostButton() {
  const queryClient = useQueryClient();
  const createPostFn = useServerFn(createPost);

  const mutation = useMutation({
    mutationFn: createPostFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });

  return (
    <button
      disabled={mutation.isPending}
      onClick={() =>
        mutation.mutate({ data: { title: 'New Post', content: '...' } })
      }
    >
      {mutation.isPending ? 'Creating...' : 'Create Post'}
    </button>
  );
}
```

## Validation Schema Composition

```ts
const baseUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

const createUserSchema = baseUserSchema.extend({
  password: z.string().min(8),
});

const updateUserSchema = baseUserSchema.partial();
```

Async validation in handlers:

```ts
const registerUser = createServerFn({ method: 'POST' })
  .inputValidator(createUserSchema)
  .handler(async ({ data }) => {
    const existing = await db.users.findUnique({
      where: { email: data.email },
    });
    if (existing) {
      return { error: 'Email already registered', code: 'CONFLICT' };
    }
    const user = await db.users.create({ data });
    return { data: user };
  });
```
