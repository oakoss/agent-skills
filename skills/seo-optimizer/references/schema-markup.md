---
title: Schema Markup Patterns
description: JSON-LD structured data patterns for Organization, Article, FAQ, Breadcrumb, and Product entities
tags: [json-ld, schema-org, structured-data, rich-results, knowledge-graph]
---

# Schema Markup Patterns

JSON-LD is the preferred format for structured data. It is embedded in a `<script>` tag and does not affect page rendering.

## Core Patterns

### Organization Schema

Define the publishing entity on every page:

```html
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Your Company",
    "url": "https://yourcompany.com",
    "logo": "https://yourcompany.com/logo.png",
    "description": "Brief description of what the organization does",
    "sameAs": [
      "https://twitter.com/yourcompany",
      "https://linkedin.com/company/yourcompany",
      "https://github.com/yourcompany"
    ],
    "contactPoint": {
      "@type": "ContactPoint",
      "contactType": "customer support",
      "url": "https://yourcompany.com/support"
    }
  }
</script>
```

### Article Schema

For blog posts, guides, and documentation pages:

```html
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "How to Optimize React Performance",
    "description": "A guide to React performance optimization techniques",
    "datePublished": "2026-01-15",
    "dateModified": "2026-01-28",
    "author": {
      "@type": "Person",
      "name": "Jane Smith",
      "url": "https://yourcompany.com/team/jane-smith",
      "jobTitle": "Senior Frontend Engineer"
    },
    "publisher": {
      "@type": "Organization",
      "name": "Your Company",
      "logo": {
        "@type": "ImageObject",
        "url": "https://yourcompany.com/logo.png"
      }
    },
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": "https://yourcompany.com/guides/react-performance"
    }
  }
</script>
```

### FAQ Schema

For pages with question-and-answer content:

```html
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is React Server Components?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "React Server Components render on the server and send only the HTML result to the client, reducing JavaScript bundle size and improving initial load performance."
        }
      },
      {
        "@type": "Question",
        "name": "How do Server Components differ from SSR?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "SSR renders the full component tree on the server and hydrates on the client. Server Components never hydrate — they stay on the server permanently, eliminating their client-side JavaScript entirely."
        }
      }
    ]
  }
</script>
```

### Breadcrumb Schema

For establishing page hierarchy in search results:

```html
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": "https://yourcompany.com"
      },
      {
        "@type": "ListItem",
        "position": 2,
        "name": "Guides",
        "item": "https://yourcompany.com/guides"
      },
      {
        "@type": "ListItem",
        "position": 3,
        "name": "React Performance"
      }
    ]
  }
</script>
```

### HowTo Schema

For step-by-step tutorials:

```html
<script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "HowTo",
    "name": "How to Set Up Lazy Loading in React",
    "description": "Step-by-step guide to implementing lazy loading with React.lazy and Suspense",
    "step": [
      {
        "@type": "HowToStep",
        "name": "Import React.lazy",
        "text": "Replace static imports with React.lazy() for route-level components."
      },
      {
        "@type": "HowToStep",
        "name": "Wrap in Suspense",
        "text": "Add a Suspense boundary with a fallback component around the lazy-loaded component."
      },
      {
        "@type": "HowToStep",
        "name": "Test loading states",
        "text": "Verify the fallback renders during chunk loading using network throttling."
      }
    ]
  }
</script>
```

## Implementation Guidelines

| Rule                                         | Rationale                               |
| -------------------------------------------- | --------------------------------------- |
| One Organization schema per site (in layout) | Establishes site-wide entity identity   |
| Article schema on every content page         | Enables rich result display in SERPs    |
| FAQ schema only when content has Q&A format  | Misuse triggers manual actions          |
| Breadcrumb schema on all non-homepage pages  | Improves SERP display and click-through |
| HowTo schema on step-by-step content only    | Enables rich step display in search     |

## Validation

Test structured data using:

- Google's Rich Results Test: validates eligibility for rich results
- Schema.org Validator: validates syntax correctness
- Lighthouse audit: checks for structured data presence and errors

Common validation errors:

| Error                   | Fix                                         |
| ----------------------- | ------------------------------------------- |
| Missing `@context`      | Add `"@context": "https://schema.org"`      |
| Invalid date format     | Use ISO 8601: `"2026-01-15"`                |
| Missing required fields | Check schema.org docs for type requirements |
| Duplicate schemas       | One schema per type per page                |
