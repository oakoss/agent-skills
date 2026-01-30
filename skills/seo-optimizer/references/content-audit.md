---
title: Content Audit Methodology
description: 30-point SEO audit scoring system covering title tags, meta descriptions, keywords, content structure, featured snippets, internal linking, and technical SEO
tags: [content-audit, seo-scoring, title-tags, snippets, linking]
---

# Content Audit Methodology

A systematic approach to evaluating and optimizing content pages for search visibility. Uses a 30-point scoring system across seven categories.

## Scoring Overview

| Category          | Max Points |
| ----------------- | ---------- |
| Title Tag         | 4          |
| Meta Description  | 4          |
| Keyword Placement | 5          |
| Content Structure | 6          |
| Featured Snippets | 4          |
| Internal Linking  | 4          |
| Technical SEO     | 3          |
| **Total**         | **30**     |

**Score interpretation:**

| Score          | Status    | Action                      |
| -------------- | --------- | --------------------------- |
| 27-30 (90%+)   | Excellent | Ready to publish            |
| 23-26 (75-89%) | Good      | Minor optimizations needed  |
| 17-22 (55-74%) | Fair      | Several improvements needed |
| 0-16 (<55%)    | Poor      | Significant work required   |

## Title Tag (4 Points)

| Check                                            | Points |
| ------------------------------------------------ | ------ |
| Length 50-60 characters                          | 1      |
| Primary keyword in first half                    | 1      |
| Contains compelling hook or benefit              | 1      |
| Includes topic qualifier (e.g., "in JavaScript") | 1      |

**Formula:** `[Concept]: [What You'll Understand] in [Topic]`

**Strong examples:**

- "Closures: How Functions Remember Their Scope in JavaScript" (58 chars)
- "Event Loop: How Async Code Actually Runs in JavaScript" (54 chars)

**Weak patterns:** Too short ("Closures"), too long (>60 chars), no hook ("JavaScript Closures"), missing qualifier.

## Meta Description (4 Points)

| Check                                                  | Points |
| ------------------------------------------------------ | ------ |
| Length 150-160 characters                              | 1      |
| Starts with action word (Learn, Understand, Discover)  | 1      |
| Contains primary keyword                               | 1      |
| Promises specific value (lists what reader will learn) | 1      |

**Formula:** `[Action word] [what it is] in [Topic]. [Specific things they'll learn]: [topic 1], [topic 2], and [topic 3].`

**Strong example:** "Learn JavaScript closures and how functions remember their scope. Covers lexical scoping, practical use cases, memory considerations, and common closure patterns." (159 chars)

## Keyword Placement (5 Points)

| Check                                 | Points |
| ------------------------------------- | ------ |
| Primary keyword in title              | 1      |
| Primary keyword in meta description   | 1      |
| Primary keyword in first 100 words    | 1      |
| Keyword in at least one H2 heading    | 1      |
| No keyword stuffing (reads naturally) | 1      |

**Density guideline:** Do not exceed 3-4 mentions of the exact phrase per 1,000 words. Use variations naturally.

## Content Structure (6 Points)

| Check                                | Points |
| ------------------------------------ | ------ |
| Opens with question hook             | 1      |
| Code example in first 200 words      | 1      |
| "What you'll learn" summary near top | 1      |
| Short paragraphs (2-4 sentences)     | 1      |
| 1,500+ words total                   | 1      |
| Key terms bolded on first mention    | 1      |

**Content length guidelines:**

| Length       | Assessment                            |
| ------------ | ------------------------------------- |
| <1,000 words | Too thin -- add depth                 |
| 1,000-1,500  | Minimum viable                        |
| 1,500-2,500  | Good                                  |
| 2,500-4,000  | Excellent                             |
| >4,000       | Consider splitting into cluster pages |

## Featured Snippets (4 Points)

| Check                                  | Points |
| -------------------------------------- | ------ |
| "What is X" has 40-60 word definition  | 1      |
| At least one H2 phrased as a question  | 1      |
| Numbered steps for "how to" content    | 1      |
| Comparison tables for "X vs Y" content | 1      |

**Snippet format mapping:**

| Query Type   | Winning Format                  |
| ------------ | ------------------------------- |
| "What is X"  | 40-60 word paragraph definition |
| "How to X"   | Numbered list or steps          |
| "X vs Y"     | Comparison table                |
| "Types of X" | Bullet list with bold labels    |

## Internal Linking (4 Points)

| Check                                          | Points |
| ---------------------------------------------- | ------ |
| 3-5 related pages linked in body text          | 1      |
| Descriptive anchor text (not "click here")     | 1      |
| Prerequisites noted with links at top          | 1      |
| Related content section at bottom with 4 links | 1      |

**Anchor text quality:**

| Weak           | Strong                                 |
| -------------- | -------------------------------------- |
| "click here"   | "React performance optimization guide" |
| "this article" | "our guide to Server Components"       |
| "read more"    | "understanding the event loop"         |

## Technical SEO (3 Points)

| Check                                                   | Points |
| ------------------------------------------------------- | ------ |
| Single H1 per page (the title only)                     | 1      |
| URL slug contains primary keyword                       | 1      |
| Page linked from at least one other page (not orphaned) | 1      |

**URL slug rules:** lowercase, hyphens not underscores, include primary keyword, under 50 characters, no IDs or random strings.

## Audit Report Template

After auditing, document findings with:

1. **Score summary** -- points per category with status
2. **Target keywords** -- primary and secondary keywords with search intent
3. **Category-by-category analysis** -- specific issues found per section
4. **Priority fixes** -- high/medium/low ranked action items
5. **Implementation checklist** -- verification steps after making fixes
