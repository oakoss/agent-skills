---
title: Content Collections
description: Defining collections with loaders and Zod schemas, querying entries, rendering content, and content-driven site patterns
tags:
  [
    content,
    collections,
    zod,
    schema,
    loader,
    getCollection,
    getEntry,
    glob,
    file,
    markdown,
  ]
---

# Content Collections

## Defining Collections

Collections are configured in `src/content.config.ts`. Each collection requires a `loader` and optionally a `schema` for type-safe validation.

```ts
import { defineCollection } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    draft: z.boolean().default(false),
    tags: z.array(z.string()).default([]),
    image: z
      .object({
        url: z.string(),
        alt: z.string(),
      })
      .optional(),
  }),
});

const authors = defineCollection({
  loader: file('src/data/authors.json'),
  schema: z.object({
    id: z.string(),
    name: z.string(),
    bio: z.string(),
    avatar: z.string().url(),
  }),
});

export const collections = { blog, authors };
```

## Built-in Loaders

### Glob Loader

Loads files matching a glob pattern from the local filesystem. Each file becomes a collection entry with an auto-generated ID based on the file path.

```ts
import { glob } from 'astro/loaders';

const docs = defineCollection({
  loader: glob({ pattern: '**/[^_]*.md', base: './src/data/docs' }),
  schema: z.object({
    title: z.string(),
    order: z.number(),
  }),
});
```

### File Loader

Loads structured data from a single JSON or YAML file. Each item in the array becomes a collection entry.

```ts
import { file } from 'astro/loaders';

const products = defineCollection({
  loader: file('src/data/products.json'),
  schema: z.object({
    id: z.string(),
    name: z.string(),
    price: z.number(),
    category: z.string(),
  }),
});
```

## Querying Collections

### Get All Entries

```astro
---
import { getCollection } from 'astro:content';

const allPosts = await getCollection('blog');
const publishedPosts = await getCollection('blog', ({ data }) => {
  return !data.draft;
});

const sortedPosts = publishedPosts.sort(
  (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
);
---
<ul>
  {sortedPosts.map((post) => (
    <li>
      <a href={`/blog/${post.id}`}>
        <h2>{post.data.title}</h2>
        <time datetime={post.data.pubDate.toISOString()}>
          {post.data.pubDate.toLocaleDateString()}
        </time>
      </a>
    </li>
  ))}
</ul>
```

### Get Single Entry

```astro
---
import { getEntry } from 'astro:content';

const post = await getEntry('blog', 'my-first-post');

if (!post) {
  return Astro.redirect('/404');
}
---
<h1>{post.data.title}</h1>
```

## Rendering Content

Use `render()` to compile Markdown/MDX content to HTML.

```astro
---
import { getEntry } from 'astro:content';

const post = await getEntry('blog', Astro.params.slug);

if (!post) {
  return Astro.redirect('/404');
}

const { Content, headings } = await post.render();
---
<article>
  <h1>{post.data.title}</h1>
  <Content />
</article>
```

## Dynamic Routes with Collections

Generate static pages from collection entries using `getStaticPaths`.

```astro
---
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  const posts = await getCollection('blog');
  return posts.map((post) => ({
    params: { slug: post.id },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content } = await post.render();
---
<article>
  <h1>{post.data.title}</h1>
  <Content />
</article>
```

## Schema Patterns

### Image Schema with Astro Image

```ts
import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      cover: image(),
    }),
});
```

### Reference Between Collections

```ts
import { defineCollection, z, reference } from 'astro:content';

const blog = defineCollection({
  schema: z.object({
    title: z.string(),
    author: reference('authors'),
    relatedPosts: z.array(reference('blog')).default([]),
  }),
});

const authors = defineCollection({
  schema: z.object({
    name: z.string(),
    bio: z.string(),
  }),
});
```

### Resolving References

```astro
---
import { getEntry } from 'astro:content';

const post = await getEntry('blog', 'my-post');
const author = await getEntry(post.data.author);
---
<p>Written by {author.data.name}</p>
```
