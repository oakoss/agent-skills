---
title: Semantic Entity SEO
description: Topic cluster architecture, intent mapping, NLP-friendly writing, and Schema.org entity definitions
tags: [semantic-seo, topic-clusters, intent-mapping, schema-org, lsi, nlp]
---

# Semantic Entity SEO

Semantic SEO focuses on user intent and relationships between concepts rather than keyword density. Search engines map content to entities in a knowledge graph.

## The Intent Map

Map every page to a specific user intent category:

| Intent        | Query Pattern          | Content Format            |
| ------------- | ---------------------- | ------------------------- |
| Informational | "How to bake a cake"   | Tutorial with steps       |
| Commercial    | "Best ovens 2026"      | Comparison with pros/cons |
| Transactional | "Buy GE Oven Model X"  | Product page with CTA     |
| Navigational  | "GE Oven support page" | Direct landing page       |

**Implementation:** Add intent as metadata or a comment in the page frontmatter. Every page should serve exactly one primary intent.

## Topic Clusters

Group related content around a central pillar page.

**Architecture:**

```text
                    ┌──────────────┐
                    │  Pillar Page │
                    │  (3000+ words) │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐
    │ Cluster A │   │ Cluster B │   │ Cluster C │
    │ (1500 words)│  │ (1500 words)│  │ (1500 words)│
    └───────────┘   └───────────┘   └───────────┘
```

**Internal linking rules:**

- Cluster articles link UP to the pillar page
- The pillar page links DOWN to each cluster article
- Cluster articles link ACROSS to related clusters where natural
- Use descriptive anchor text (not "click here")

**Example cluster for "React Performance":**

| Role    | Page                    | Target Keyword                      |
| ------- | ----------------------- | ----------------------------------- |
| Pillar  | React Performance Guide | react performance                   |
| Cluster | React Memo and useMemo  | react memoization                   |
| Cluster | React Lazy Loading      | react code splitting                |
| Cluster | React Profiler          | react profiling tools               |
| Cluster | React Server Components | react server components performance |

## Schema.org for Entities

Use structured data to explicitly define entities for the knowledge graph.

**Organization schema** -- define who you are:

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Acme Corp",
  "url": "https://acme.com",
  "logo": "https://acme.com/logo.png",
  "sameAs": ["https://twitter.com/acmecorp", "https://github.com/acmecorp"]
}
```

**FAQ schema** -- define the questions you answer:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is lazy loading?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Lazy loading defers resource initialization until needed."
      }
    }
  ]
}
```

**Breadcrumb schema** -- define the page hierarchy:

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Guides",
      "item": "https://example.com/guides"
    },
    { "@type": "ListItem", "position": 3, "name": "Performance" }
  ]
}
```

## NLP-Friendly Writing

Write in patterns that NLP models parse reliably.

**Active sentences:** Subject, verb, object order. Avoid passive voice for key definitions.

```text
Strong: "React Server Components render on the server."
Weak:   "Rendering on the server is done by React Server Components."
```

**LSI terms:** Include terms that naturally co-occur in quality discussions of the topic. Do not force them; weave them in where they fit.

**Consistent terminology:** Pick one term and use it throughout. Do not alternate between "endpoint," "route," and "URL" for the same concept.

## Content Freshness

AI-powered search engines favor current data.

**Refresh protocol:** Update critical articles every 6 months with:

- Current statistics and benchmarks
- Updated tool versions and recommendations
- New patterns that have emerged since publication
- Removal of deprecated approaches
