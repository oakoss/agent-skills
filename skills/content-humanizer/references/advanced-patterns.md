---
title: Advanced Patterns
description: E-E-A-T signals, burstiness, perplexity variation, paragraph rhythm, and section-level structural variation for authentic human writing
tags:
  [
    eeat,
    experience,
    expertise,
    authoritativeness,
    trustworthiness,
    burstiness,
    perplexity,
    rhythm,
    structural-variation,
    ai-detection,
  ]
---

# Advanced Patterns

## E-E-A-T Signals in Writing

E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) is the framework Google's quality raters use to evaluate content. AI-generated prose fails E-E-A-T because it lacks first-hand experience and defaults to generic authority claims. Injecting genuine E-E-A-T signals makes content both more human and more valuable.

### Experience: The "I Was There" Factor

First-person experience is the hardest signal for AI to fake. Content that references specific events, timelines, and personal observations reads as authentic.

```text
Before (generic AI claim):
Setting up a monorepo can be challenging for large teams.

After (experience signal):
Last month, I migrated a 40-person team to Turborepo. The first two days went
smoothly. Day three, we hit three circular dependencies that broke every CI
pipeline. Here's what we learned fixing them at 11pm on a Wednesday.
```

Experience signals to embed:

```text
- Specific timelines: "Last quarter," "During the 2024 migration," "After six months of running this in production"
- Named tools and versions: "React 19.1," "PostgreSQL 16," "the v3.2 release"
- Quantified outcomes: "Cut build time from 12 minutes to 90 seconds"
- Failure stories: What went wrong and what you learned
- Team context: Size, constraints, deadlines that shaped decisions
```

### Expertise: Technical Depth Over Breadth

AI produces broad, surface-level coverage. Expert writing goes deep on specifics that only someone with real knowledge would mention.

```text
Before (surface-level):
Database indexing improves query performance significantly.

After (expert depth):
A composite index on (user_id, created_at DESC) dropped our dashboard query
from 3.2 seconds to 18ms. The key was matching the index order to the WHERE
clause. We tried indexing created_at alone first and saw almost no improvement
because the planner still did a sequential scan on user_id.
```

Expertise markers:

```text
- Specific error messages and how to interpret them
- Performance numbers from real systems
- Trade-offs that only emerge in practice
- References to specific GitHub issues, RFCs, or changelogs
- Mention of approaches that were tried and abandoned, with reasons
```

### Authoritativeness: Source Quality

AI cites vague authority ("experts say," "studies show"). Authoritative writing links to primary sources and names specific people or organizations.

```text
Before (vague authority):
Research shows that page load speed impacts conversion rates.

After (authoritative sourcing):
Google's 2024 Core Web Vitals report found that pages meeting all three
thresholds see 24% lower bounce rates. Specifically, an LCP under 2.5 seconds
correlated with a 7% lift in conversions for e-commerce sites.
```

Authoritativeness patterns:

```text
- Link to official documentation, not aggregator blog posts
- Reference specific studies with authors and dates
- Quote recognized practitioners with attribution
- Cite version numbers, release notes, and changelogs
```

### Trustworthiness: Transparency and Honesty

Trust is the foundation of E-E-A-T. Trustworthy content acknowledges limitations, discloses context, and avoids overselling.

```text
Before (overselling):
This approach works perfectly for all team sizes and eliminates deployment risk entirely.

After (trustworthy):
This approach works well for teams of 5-20 developers. Larger teams may need a
dedicated platform team to maintain the pipeline. We've seen two production
incidents in 18 months, both caused by misconfigured environment variables
rather than the deployment process itself.
```

Trust signals:

```text
- "Last updated" dates on content
- Author attribution with verifiable credentials
- Honest limitations: "This doesn't work for X"
- Disclosure of AI assistance when applicable
- Concrete numbers instead of superlatives
```

## Burstiness: Sentence Length Variation

Burstiness measures variation in sentence length and complexity across a document. AI-generated text has low burstiness, meaning sentences cluster around similar lengths. Human writing has high burstiness, mixing short punchy sentences with longer complex ones.

### Why Burstiness Matters

AI detection tools like GPTZero use burstiness as a primary signal. Low burstiness (uniform sentence length) flags content as machine-generated. Human writing naturally varies because people emphasize different ideas with different rhythms.

### Measuring Burstiness

Count the words in each sentence of a paragraph. AI-typical output looks like this:

```text
Low burstiness (AI-typical):
[14] [16] [15] [13] [16]   ← all sentences cluster around 14-16 words

High burstiness (human):
[4] [22] [8] [31] [3]      ← wide variation from 3 to 31 words
```

### The 1-2 Punch Technique

Follow a long, detailed sentence with a short declarative one. The contrast creates emphasis and mimics natural speech rhythm.

```text
Before (uniform):
The caching layer intercepts requests before they reach the database server.
It stores frequently accessed data in memory for faster retrieval times.
The system automatically invalidates stale entries when the source data changes.

After (bursty):
The caching layer sits between your application and the database, intercepting
requests and serving frequently accessed data from memory so the database
never sees repeated queries for the same rows. Stale entries invalidate
automatically. No manual cache management required.
```

### Fragment Bursts

Intentional sentence fragments increase burstiness and add punch when used sparingly.

```text
Before:
The deployment completed without any errors or downtime.

After:
The deployment completed without errors. Zero downtime. Not even a blip on the
status page.
```

### Internal Punctuation for Complexity Variation

Dashes, semicolons, and colons create complex sentence structures that vary the rhythm without requiring more sentences.

```text
Before:
The API supports both REST and GraphQL endpoints. Teams can choose the format
that works best for their use case. Both formats return the same data.

After:
The API supports both REST and GraphQL -- teams pick whichever fits their
stack. Both return identical data; the only difference is how you query it.
```

## Perplexity: Word Choice Unpredictability

Perplexity measures how predictable the next word is in a sequence. AI chooses high-probability words, producing text with low perplexity. Human writing uses unexpected but appropriate word choices, idioms, and domain-specific vocabulary that increase perplexity.

### Formulaic Phrases to Replace

AI gravitates toward the same high-probability phrases. Replace them with specific, less predictable alternatives.

```text
AI-typical (low perplexity)    → Human alternative (higher perplexity)
"comprehensive solution"       → "the fix that actually stuck"
"significant improvement"      → "a 40% drop in error rates"
"in the ever-evolving          → [delete entirely]
  landscape"
"dive into"                    → "break down" / "walk through" / "unpack"
"revolutionize"                → [use a specific verb for what changed]
"game-changer"                 → [describe the actual impact]
"best practices"               → "patterns that held up in production"
"leverage"                     → "use" / "lean on" / "tap into"
```

### Domain-Specific Vocabulary

Replace generic terms with vocabulary specific to the audience and subject matter. A database engineer says "query planner" not "processing system." A frontend developer says "hydration mismatch" not "rendering error."

```text
Before (generic):
The system processes data and produces results efficiently.

After (domain-specific):
The pipeline ingests events from Kafka, deduplicates against a Redis
bloom filter, and materializes aggregates into ClickHouse. End-to-end
latency sits under 200ms at the 99th percentile.
```

### Concrete Verbs Over Abstract Ones

AI defaults to abstract, safe verbs. Swap them for concrete verbs that paint a picture.

```text
AI-typical: "improves," "enhances," "facilitates," "enables"

Human alternatives:
- "improves" → "cuts," "trims," "shrinks," "boosts," "tightens"
- "enables" → "unlocks," "opens up," "hands you," "lets"
- "facilitates" → "brokers," "bridges," "wires together"
```

### Idiomatic Language

Idioms, colloquialisms, and metaphors are high-perplexity signals that AI rarely produces naturally.

```text
Before:
The legacy codebase presented significant challenges for the team.

After:
The legacy codebase was held together with duct tape and optimism. Every
refactor felt like playing Jenga with load-bearing spaghetti.
```

Use idioms sparingly and match them to the formality level. A casual blog post tolerates more than a technical white paper.

## Paragraph Rhythm and Pacing

AI writes paragraphs of uniform length (typically three to five sentences each). Human writing varies paragraph length deliberately to control pacing and emphasis.

### The One-Sentence Paragraph

A single-sentence paragraph stands out. It creates a pause, signals importance, and breaks the visual monotony of uniform blocks.

```text
Before (uniform blocks):
Authentication uses OAuth 2.0 tokens. The system supports both authorization
code and client credentials flows. Tokens expire after 24 hours and must be
refreshed using the dedicated endpoint. The refresh process is automatic for
most SDK users.

Rate limiting protects the API from abuse. Each account receives 1,000 requests
per minute. Enterprise accounts can request higher limits. The system returns a
429 status code when limits are exceeded.

After (varied paragraph length):
Authentication runs on OAuth 2.0, supporting both authorization code and client
credentials flows. Tokens last 24 hours. The SDK handles refresh automatically.

What about rate limits?

Each account gets 1,000 requests per minute. Enterprise teams raise that
ceiling from their settings page -- no support ticket needed. Hit the limit
and the API returns a 429 with a Retry-After header.
```

### Pacing Through Paragraph Length

Short paragraphs speed the reader up. Long paragraphs slow them down for complex ideas. Alternate to keep the reading experience engaging.

```text
Pattern to follow:
- Medium paragraph (3-4 sentences): introduce a concept
- Short paragraph (1 sentence): make a key point land
- Long paragraph (5-6 sentences): develop a complex idea with nuance
- Short paragraph (1 sentence): transition or emphasize
```

### Opening Variation

AI opens every paragraph the same way: topic sentence, supporting detail, conclusion. Break this pattern by varying how paragraphs begin.

```text
Paragraph openers to rotate:
- A question: "What happens when the cache misses?"
- A specific example: "Last Tuesday, our staging environment caught fire."
- A bold claim: "Most rate limiters are configured wrong."
- A continuation: "That's the easy part."
- A number: "Three things break during every migration."
```

## Section-Level Structural Variation

AI produces sections that mirror each other: same length, same heading depth, same internal structure. Human-written documents vary section structure based on the complexity and nature of each topic.

### Vary Section Length

Not every section deserves equal treatment. Some topics need three paragraphs; others need ten. Let the content dictate the length rather than imposing uniformity.

```text
AI pattern:
## Feature A (4 paragraphs)
## Feature B (4 paragraphs)
## Feature C (4 paragraphs)

Human pattern:
## Feature A (2 paragraphs -- it's straightforward)
## Feature B (8 paragraphs -- it's complex and deserves depth)
## Feature C (1 paragraph + a code example -- best shown, not explained)
```

### Mix Content Types Within Sections

AI defaults to prose paragraphs in every section. Human writers mix prose, code blocks, tables, callouts, and examples based on what communicates best.

```text
Section structure options:
- Prose only: for narrative explanations
- Prose + code: for technical walkthroughs
- Table: for comparisons and quick reference
- Code + annotation: for API examples
- Single example with no preamble: when the code speaks for itself
```

### Asymmetric Heading Depth

AI creates perfectly symmetrical heading hierarchies. Human documents go deeper on complex topics and stay shallow on simple ones.

```text
AI pattern (symmetrical):
## Authentication
### Setup
### Configuration
## Authorization
### Setup
### Configuration

Human pattern (asymmetric):
## Authentication
### Token Flow
### Refresh Handling
### Common Errors
## Authorization
(covered in two paragraphs, no subheadings needed)
```

The goal is structure that serves the reader, not structure that satisfies a template.
