---
title: SEO and Head Management
description: Document head management using the head property on routes for meta tags, Open Graph, favicons, stylesheets, and per-route SEO
tags:
  [
    seo,
    head,
    meta,
    title,
    open-graph,
    favicon,
    links,
    stylesheet,
    viewport,
    charset,
    og,
    twitter,
  ]
---

# SEO and Head Management

## Root Route Head Configuration

Set global meta tags, favicons, and stylesheets on the root route using the `head` property:

```tsx
import appCss from '@/styles/app.css?url';

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { title: 'My App' },
      { name: 'description', content: 'A full-stack React application' },
    ],
    links: [
      { rel: 'stylesheet', href: appCss },
      { rel: 'icon', href: '/favicon.ico' },
      {
        rel: 'apple-touch-icon',
        sizes: '180x180',
        href: '/apple-touch-icon.png',
      },
      {
        rel: 'icon',
        type: 'image/png',
        sizes: '32x32',
        href: '/favicon-32x32.png',
      },
      { rel: 'manifest', href: '/site.webmanifest' },
    ],
  }),
  component: RootComponent,
});
```

## Per-Route Head

Override or extend head tags on individual routes:

```tsx
export const Route = createFileRoute('/blog/$slug')({
  loader: async ({ params }) => {
    const post = await fetchPost(params.slug);
    if (!post) throw notFound();
    return { post };
  },
  head: ({ loaderData }) => ({
    meta: [
      { title: loaderData.post.title },
      { name: 'description', content: loaderData.post.excerpt },
    ],
  }),
});
```

## Open Graph and Twitter Cards

```tsx
export const Route = createFileRoute('/blog/$slug')({
  loader: async ({ params }) => {
    const post = await fetchPost(params.slug);
    if (!post) throw notFound();
    return { post };
  },
  head: ({ loaderData }) => ({
    meta: [
      { title: loaderData.post.title },
      { name: 'description', content: loaderData.post.excerpt },
      { property: 'og:title', content: loaderData.post.title },
      { property: 'og:description', content: loaderData.post.excerpt },
      { property: 'og:image', content: loaderData.post.coverImage },
      { property: 'og:type', content: 'article' },
      { name: 'twitter:card', content: 'summary_large_image' },
      { name: 'twitter:title', content: loaderData.post.title },
      { name: 'twitter:description', content: loaderData.post.excerpt },
      { name: 'twitter:image', content: loaderData.post.coverImage },
    ],
  }),
});
```

## SEO Helper Function

Create a reusable helper to reduce boilerplate:

```ts
type SeoOptions = {
  title: string;
  description: string;
  image?: string;
  type?: string;
};

export function seo({
  title,
  description,
  image,
  type = 'website',
}: SeoOptions) {
  const tags: Array<Record<string, string>> = [
    { title },
    { name: 'description', content: description },
    { property: 'og:title', content: title },
    { property: 'og:description', content: description },
    { property: 'og:type', content: type },
    {
      name: 'twitter:card',
      content: image ? 'summary_large_image' : 'summary',
    },
    { name: 'twitter:title', content: title },
    { name: 'twitter:description', content: description },
  ];

  if (image) {
    tags.push(
      { property: 'og:image', content: image },
      { name: 'twitter:image', content: image },
    );
  }

  return tags;
}
```

Usage:

```tsx
export const Route = createFileRoute('/blog/$slug')({
  loader: async ({ params }) => {
    const post = await fetchPost(params.slug);
    if (!post) throw notFound();
    return { post };
  },
  head: ({ loaderData }) => ({
    meta: [
      ...seo({
        title: loaderData.post.title,
        description: loaderData.post.excerpt,
        image: loaderData.post.coverImage,
        type: 'article',
      }),
    ],
  }),
});
```

## Head Property Reference

| Property | Type                            | Description                          |
| -------- | ------------------------------- | ------------------------------------ |
| `meta`   | `Array<Record<string, string>>` | Meta tags for the page               |
| `links`  | `Array<Record<string, string>>` | Link elements (CSS, icons, manifest) |

Common meta tag patterns:

| Pattern                        | Description              |
| ------------------------------ | ------------------------ |
| `{ title: '...' }`             | Page title               |
| `{ charset: 'utf-8' }`         | Character encoding       |
| `{ name: 'viewport', ... }`    | Responsive viewport      |
| `{ name: 'description', ... }` | Page description         |
| `{ property: 'og:...', ... }`  | Open Graph tags          |
| `{ name: 'twitter:...', ... }` | Twitter Card tags        |
| `{ name: 'robots', ... }`      | Search engine directives |
