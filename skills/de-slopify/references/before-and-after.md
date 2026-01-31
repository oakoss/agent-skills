---
title: Before and After Examples
description: Side-by-side examples showing how to fix common AI writing patterns in documentation, READMEs, and technical prose
tags: [examples, emdash, enthusiasm, contrast, robotic, authentic, rewrite]
---

# Before and After Examples

## Emdash Chain

Three or more emdashes in a single sentence is one of the strongest AI writing signals.

```text
BEFORE:
This tool--which we built from scratch--handles everything automatically--from parsing to output.

AFTER:
This tool handles everything automatically, from parsing to output. We built it from scratch.
```

The fix restructures the sentence rather than swapping punctuation one-for-one.

## "Here's Why" Lead-In

```text
BEFORE:
We chose Rust for this component. Here's why: performance matters, and Rust delivers.

AFTER:
We chose Rust for this component because performance matters.
```

Delete the lead-in and fold the explanation into the previous sentence.

## Contrast Formula

```text
BEFORE:
It's not just a linter; it's a complete code quality system.

AFTER:
This complete code quality system goes beyond basic linting.
```

Alternative fix when the contrast is the actual point:

```text
BEFORE:
It's not about writing less code, it's about writing the right code.

AFTER:
Writing less code is not the goal. Writing the right code is.
```

## Forced Enthusiasm in Getting Started

```markdown
BEFORE:

# Getting Started

Let's dive in! We're excited to help you get up and running with our amazing tool.
In this guide, we'll walk you through everything you need to know.

AFTER:

# Getting Started

Install the CLI and run your first command in under a minute.
```

Delete the enthusiasm. Delete the meta-commentary about the guide. Start with what the reader does.

## Robotic vs. Authentic Technical Writing

```text
BEFORE:
Artificial intelligence is revolutionizing the way we write code. It provides
efficiency and reduces the time required for development tasks. However, it is
important to maintain quality. In this comprehensive guide, we'll explore best
practices for leveraging AI in your workflow.

AFTER:
Raw AI code is often a mess of predictable patterns and dropped context. Speed
is a trap if you aren't auditing for intent.
```

The before version has five AI tells: "revolutionizing", "leveraging", "comprehensive guide", "we'll explore", and the passive hedge "it is important to maintain quality." The after version has zero.

## Pseudo-Profound README Opener

```markdown
BEFORE:

# MyLib

At its core, MyLib is a lightweight, developer-friendly library that
fundamentally transforms how you handle state management. In the
ever-evolving landscape of frontend development, it's worth noting
that MyLib stands out.

AFTER:

# MyLib

A 2KB state manager for React. Replaces useState + useContext for
cross-component state without the boilerplate.
```

Delete every sentence that says nothing specific. Replace with facts: size, what it replaces, what pain it removes.

## Over-Hedged Technical Claim

```text
BEFORE:
It's important to note that, while there are many approaches to caching,
it's worth considering that Redis might be a good option for your use case,
depending on your specific requirements and constraints.

AFTER:
Use Redis. It handles our caching patterns and runs on every cloud provider.
If your data fits in memory, it is the default choice.
```

Three hedges in one sentence is a strong tell. Pick a position and state it.

## Uniform Sentence Length

```text
BEFORE:
The middleware validates incoming requests against the schema. It rejects
malformed payloads with a descriptive error message. The error includes
the field name and the expected type. This helps developers fix issues
quickly without checking the documentation.

AFTER:
The middleware validates requests against the schema. Malformed payloads
get rejected with an error that names the bad field and its expected type.
No need to check the docs.
```

The before version has four sentences of nearly identical length (9-11 words each). The after version mixes a medium sentence, a longer one, and a short punchy closer.

## API Documentation Intro

```text
BEFORE:
Welcome to the API documentation! In this comprehensive guide, we'll walk
you through all the endpoints available in our powerful and flexible API.
Whether you're a seasoned developer or just getting started, you'll find
everything you need to integrate seamlessly with our platform.

AFTER:
Base URL: https://api.example.com/v2

All endpoints require an API key in the Authorization header. Rate limit:
1000 requests per minute. Responses use JSON.
```

API docs should open with the base URL and auth requirements, not a welcome message.

## Blog Post Closer

```text
BEFORE:
In conclusion, we've explored three key patterns for handling errors in
distributed systems. By leveraging these approaches, you can build more
resilient applications. We hope this guide has been helpful on your
journey toward better error handling!

AFTER:
Retry with backoff, use circuit breakers at service boundaries, and
dead-letter failed messages for manual review. That covers 90% of
production error scenarios.
```

Replace the meta-summary with the actual summary. Delete "In conclusion", "we've explored", "leveraging", and "journey."

## CONTRIBUTING.md Section

```markdown
BEFORE:

## How to Contribute

We're thrilled that you want to contribute to our project! Your contributions
help make this project better for everyone. Here's how you can get started on
your contribution journey:

1. Fork the repository
2. Create a feature branch
3. Make your changes

AFTER:

## How to Contribute

1. Fork the repository
2. Create a branch from `main`
3. Make your changes and add tests
4. Open a PR against `main`

We review PRs within two business days.
```

Delete the emotional opener. Add the missing step (PR). Add the detail that actually matters (review timeline).

## Changelog Entry

```text
BEFORE:
We're excited to announce that we've added a powerful new feature that
revolutionizes how you handle file uploads! This game-changing enhancement
provides a seamless experience for your users.

AFTER:
Added: Resumable file uploads via tus protocol. Files over 100MB upload
in chunks with automatic retry on network failure.
```

Changelogs should state what changed, how it works, and what threshold triggers it. Not excitement.
