---
title: Semantic HTML and Structure
description: Document landmarks, heading hierarchy, element selection for interactive and grouping elements, and skip link implementation
tags: [semantic-html, landmarks, headings, skip-links, document-structure]
---

# Semantic HTML and Structure

Use the right element. Semantic elements provide built-in keyboard support and screen reader announcements.

## Semantic vs Non-Semantic

```html
<!-- WRONG: divs with onClick -->
<div onclick="submit()">Submit</div>
<div onclick="navigate()">Next page</div>

<!-- CORRECT: semantic elements -->
<button type="submit">Submit</button>
<a href="/next">Next page</a>
```

## Document Structure and Landmarks

```html
<header>
  <nav aria-label="Main navigation">...</nav>
</header>

<main id="main-content">
  <h1>Page Title</h1>
  <h2>Section 1</h2>
  <h3>Subsection 1.1</h3>
  <h2>Section 2</h2>

  <article>...</article>
  <aside>...</aside>
</main>

<footer>...</footer>
```

Heading hierarchy must not skip levels (h1 then h3 with no h2).

## ARIA: Only When HTML Cannot Express the Pattern

```html
<!-- WRONG: unnecessary ARIA -->
<button role="button">Click me</button>

<!-- CORRECT: ARIA fills a semantic gap -->
<div role="dialog" aria-labelledby="title" aria-modal="true">
  <h2 id="title">Confirm action</h2>
</div>

<!-- BETTER: native HTML when available -->
<dialog aria-labelledby="title">
  <h2 id="title">Confirm action</h2>
</dialog>
```

## Skip Links

```html
<a href="#main-content" class="skip-link">Skip to main content</a>

<nav>...</nav>

<main id="main-content" tabindex="-1">...</main>
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--primary);
  color: white;
  padding: 8px 16px;
  z-index: 9999;
}

.skip-link:focus {
  top: 0;
}
```
