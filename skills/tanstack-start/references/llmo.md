---
title: LLM Optimization (LLMO)
description: Structured data, JSON-LD schemas, llms.txt, machine-readable endpoints, and content patterns for AI citation and discovery in TanStack Start
tags:
  [
    llmo,
    aio,
    geo,
    structured-data,
    json-ld,
    schema-org,
    llms-txt,
    ai-optimization,
  ]
---

## What is LLMO

LLM Optimization (LLMO) — also called AI Optimization (AIO) or Generative Engine Optimization (GEO) — structures content so AI systems (ChatGPT, Claude, Perplexity) can accurately understand, cite, and recommend it.

### LLMO vs SEO

| Aspect         | SEO                         | LLMO                                   |
| -------------- | --------------------------- | -------------------------------------- |
| Goal           | Rank in search results      | Be cited/recommended by AI             |
| Audience       | Search engine crawlers      | LLM training and retrieval systems     |
| Key signals    | Links, keywords, page speed | Structured data, clarity, authority    |
| Content format | Optimized for snippets      | Optimized for extraction and synthesis |

Many LLMO best practices overlap with SEO. Clear structure, authoritative content, and good metadata help both.

## TanStack Start LLMO Features

- **SSR** — AI crawlers see fully rendered content
- **JSON-LD via `head.scripts`** — Machine-readable structured data on every route
- **Server routes** — Create machine-readable endpoints (APIs, feeds, `llms.txt`)
- **Head management** — Meta tags that AI systems parse for context

## Structured Data (JSON-LD)

Use `head.scripts` with `type: 'application/ld+json'` to embed schema.org data.

### Article Schema

```tsx
export const Route = createFileRoute('/posts/$postId')({
  loader: async ({ params }) => {
    const post = await fetchPost(params.postId);
    return { post };
  },
  head: ({ loaderData }) => ({
    meta: [{ title: loaderData.post.title }],
    scripts: [
      {
        type: 'application/ld+json',
        children: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'Article',
          headline: loaderData.post.title,
          description: loaderData.post.excerpt,
          image: loaderData.post.coverImage,
          author: {
            '@type': 'Person',
            name: loaderData.post.author.name,
            url: loaderData.post.author.url,
          },
          publisher: {
            '@type': 'Organization',
            name: 'My Company',
            logo: {
              '@type': 'ImageObject',
              url: 'https://myapp.com/logo.png',
            },
          },
          datePublished: loaderData.post.publishedAt,
          dateModified: loaderData.post.updatedAt,
        }),
      },
    ],
  }),
  component: PostPage,
});
```

### Product Schema

```tsx
export const Route = createFileRoute('/products/$productId')({
  loader: async ({ params }) => {
    const product = await fetchProduct(params.productId);
    return { product };
  },
  head: ({ loaderData }) => ({
    meta: [{ title: loaderData.product.name }],
    scripts: [
      {
        type: 'application/ld+json',
        children: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'Product',
          name: loaderData.product.name,
          description: loaderData.product.description,
          image: loaderData.product.images,
          brand: {
            '@type': 'Brand',
            name: loaderData.product.brand,
          },
          offers: {
            '@type': 'Offer',
            price: loaderData.product.price,
            priceCurrency: 'USD',
            availability: loaderData.product.inStock
              ? 'https://schema.org/InStock'
              : 'https://schema.org/OutOfStock',
          },
          aggregateRating: loaderData.product.rating
            ? {
                '@type': 'AggregateRating',
                ratingValue: loaderData.product.rating,
                reviewCount: loaderData.product.reviewCount,
              }
            : undefined,
        }),
      },
    ],
  }),
  component: ProductPage,
});
```

### Organization and Website Schema

Add to the root route for site-wide context:

```tsx
export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    ],
    scripts: [
      {
        type: 'application/ld+json',
        children: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'WebSite',
          name: 'My App',
          url: 'https://myapp.com',
          publisher: {
            '@type': 'Organization',
            name: 'My Company',
            url: 'https://myapp.com',
            logo: 'https://myapp.com/logo.png',
            sameAs: [
              'https://twitter.com/mycompany',
              'https://github.com/mycompany',
            ],
          },
        }),
      },
    ],
  }),
  component: RootComponent,
});
```

### FAQ Schema

Particularly effective for LLMO — AI systems often extract Q&A pairs:

```tsx
export const Route = createFileRoute('/faq')({
  loader: async () => {
    const faqs = await fetchFAQs();
    return { faqs };
  },
  head: ({ loaderData }) => ({
    meta: [{ title: 'Frequently Asked Questions' }],
    scripts: [
      {
        type: 'application/ld+json',
        children: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'FAQPage',
          mainEntity: loaderData.faqs.map((faq) => ({
            '@type': 'Question',
            name: faq.question,
            acceptedAnswer: {
              '@type': 'Answer',
              text: faq.answer,
            },
          })),
        }),
      },
    ],
  }),
  component: FAQPage,
});
```

## Common Schema Types

| Schema Type           | Use Case              | Key Properties                  |
| --------------------- | --------------------- | ------------------------------- |
| `Article`             | Blog posts, news      | headline, author, datePublished |
| `Product`             | E-commerce items      | name, offers, aggregateRating   |
| `FAQPage`             | Q&A content           | mainEntity (Question + Answer)  |
| `WebSite`             | Root route, site-wide | name, url, publisher            |
| `Organization`        | Company info          | name, logo, sameAs              |
| `HowTo`               | Tutorials, guides     | step, tool, supply              |
| `SoftwareApplication` | App listings          | applicationCategory, offers     |
| `BreadcrumbList`      | Navigation path       | itemListElement                 |

## Machine-Readable Endpoints

Create API endpoints that AI systems and developers consume directly:

```ts
export const Route = createFileRoute('/api/products')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const url = new URL(request.url);
        const category = url.searchParams.get('category');
        const products = await fetchProducts({ category });

        return Response.json({
          '@context': 'https://schema.org',
          '@type': 'ItemList',
          itemListElement: products.map((product, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            item: {
              '@type': 'Product',
              name: product.name,
              description: product.description,
              url: `https://myapp.com/products/${product.id}`,
            },
          })),
        });
      },
    },
  },
});
```

## llms.txt

A `llms.txt` file (similar to `robots.txt`) provides guidance to AI systems about your site:

```ts
export const Route = createFileRoute('/llms.txt' as any)({
  server: {
    handlers: {
      GET: async () => {
        const content = `# My App

> My App is a platform for building modern web applications.

## Documentation
- Getting Started: https://myapp.com/docs/getting-started
- API Reference: https://myapp.com/docs/api

## Key Facts
- Built with TanStack Start
- Full TypeScript support
- SSR and streaming out of the box

## Contact
- Website: https://myapp.com
- GitHub: https://github.com/mycompany/myapp
`;

        return new Response(content, {
          headers: { 'Content-Type': 'text/plain' },
        });
      },
    },
  },
});
```

## Content Best Practices

### Clear, Factual Statements

AI systems extract factual claims. Make key information explicit:

```tsx
function ProductDetails({ product }: { product: Product }) {
  return (
    <article>
      <h1>{product.name}</h1>
      <p>
        {product.name} is a {product.category} made by {product.brand}. It costs
        ${product.price} and is available in {product.colors.join(', ')}.
      </p>
    </article>
  );
}
```

### Hierarchical Heading Structure

AI systems use heading hierarchy to understand content organization. Never skip heading levels.

### Authoritative Attribution

Include author information and sources — AI systems consider authority signals:

```tsx
export const Route = createFileRoute('/posts/$postId')({
  head: ({ loaderData }) => ({
    meta: [
      { title: loaderData.post.title },
      { name: 'author', content: loaderData.post.author.name },
      {
        property: 'article:author',
        content: loaderData.post.author.profileUrl,
      },
      {
        property: 'article:published_time',
        content: loaderData.post.publishedAt,
      },
    ],
  }),
  component: PostPage,
});
```

## Monitoring AI Citations

- **Test with AI assistants** — ask ChatGPT, Claude, and Perplexity about your product/content
- **Monitor brand mentions** — track how AI systems describe your offerings
- **Validate structured data** — use Google's Rich Results Test and Schema.org Validator
- **Check AI search engines** — monitor presence in Perplexity, Bing Chat, and Google AI Overviews
