---
title: Tone and Voice
description: Brand voice consistency, audience adaptation, formality levels, and empathy without fluff
tags: [tone, voice, brand, audience, formality, empathy, consistency, persona]
---

# Tone and Voice

## Voice vs. Tone

Voice is the consistent personality behind writing. It stays the same across all content. Tone shifts based on context, the way a person speaks differently at a conference than at a dinner table.

| Concept | Definition                                                      | Changes?                             |
| ------- | --------------------------------------------------------------- | ------------------------------------ |
| Voice   | The personality, values, and perspective of the writer or brand | Rarely; evolves slowly               |
| Tone    | The emotional quality applied to a specific piece               | Per piece, per audience, per context |

## Defining Voice Before Editing

Humanization fails without a target voice. Before rewriting AI-generated content, define these three parameters.

### 1. Persona

Who is speaking? A startup founder? A technical lead? A product team? The persona determines word choice, cultural references, and level of authority.

```text
Before (generic AI voice):
Our solution empowers teams to streamline their workflows and achieve optimal productivity through innovative automation capabilities.

After (startup founder persona):
We built this because our own team wasted three hours a day on manual handoffs. The automation handles the boring parts so your team ships faster.

After (technical lead persona):
The workflow engine chains tasks via a DAG scheduler. Define dependencies in YAML, and the runtime handles parallelization and retry logic.
```

### 2. Audience

Write for the reader's knowledge level and priorities. Marketing copy for executives differs from onboarding docs for developers.

| Audience           | Priorities                           | Language Level                     |
| ------------------ | ------------------------------------ | ---------------------------------- |
| C-suite executives | ROI, risk, competitive advantage     | Business language, minimal jargon  |
| Product managers   | Roadmap impact, user outcomes        | Feature-benefit language           |
| Developers         | Implementation, API surface, gotchas | Technical precision, code examples |
| End users          | Getting tasks done quickly           | Plain language, step-by-step       |

```text
Same feature, different audiences:

Executive: The platform reduced churn by 18% in Q3 by surfacing at-risk accounts before they cancel.

Product manager: At-risk scoring triggers automated outreach sequences 14 days before predicted churn, giving CS teams time to intervene.

Developer: The churn model runs nightly via a cron job, scoring accounts on a 0-100 scale based on login frequency, feature adoption, and support ticket volume. Scores land in the accounts table and fire a webhook when they cross the threshold you configure.
```

### 3. Formality Level

Formality is a spectrum. Pick a point and stay consistent within each piece.

| Level          | Characteristics                                   | Use For                                              |
| -------------- | ------------------------------------------------- | ---------------------------------------------------- |
| Formal         | No contractions, complete sentences, third person | Legal content, enterprise proposals, compliance docs |
| Professional   | Occasional contractions, second person allowed    | Blog posts, product updates, case studies            |
| Conversational | Contractions, fragments, first person             | Newsletters, social media, community posts           |
| Casual         | Slang acceptable, humor encouraged                | Internal comms, developer blogs, social threads      |

```text
Formal: The organization has implemented a revised policy regarding remote work eligibility.
Professional: We've updated our remote work policy. Here's what changed.
Conversational: Remote work rules just got simpler. Let's walk through it.
Casual: New remote policy dropped. TL;DR: more flexibility, fewer hoops.
```

## Voice Consistency Checks

### The Swap Test

Take three paragraphs from different sections. If you swapped their order, would the voice feel consistent? If one paragraph sounds like a press release and another sounds like a blog post, the voice drifted.

### The Attribution Test

Cover the byline. Could a regular reader guess who wrote this? Strong voice is recognizable. Generic voice could belong to anyone.

### Consistency Markers

Track these elements across a piece to maintain voice:

| Marker              | What to Check                                        |
| ------------------- | ---------------------------------------------------- |
| Person              | First, second, or third person; stay consistent      |
| Contractions        | All or none within the same piece                    |
| Sentence complexity | Maintain a similar range throughout                  |
| Jargon density      | Same level of technical language start to finish     |
| Humor               | If present in the intro, should appear elsewhere too |

## Empathy Without Fluff

AI-generated content often attempts empathy through hollow phrases ("We understand how frustrating this can be"). Genuine empathy demonstrates understanding through specifics.

### Show, Don't Claim

```text
Before (hollow empathy):
We understand that dealing with data migrations can be challenging. That's why we've built a comprehensive solution to help you navigate this complex process.

After (demonstrated empathy):
Data migrations break things. We've seen teams lose weekends to charset mismatches and orphaned foreign keys. The migration tool validates your schema before touching production, rolls back on any failure, and logs every operation so you're never guessing what happened.
```

### Acknowledge Real Pain Points

```text
Before:
We're committed to providing the best possible experience for our users.

After:
The old dashboard was slow. Pages took four seconds to load on average. We rewrote the rendering pipeline and cut that to under 400ms.
```

### Avoid Patronizing Positivity

```text
Before:
Great news! You're almost there! Just a few more steps and you'll be all set!

After:
Three steps left. Estimated time: two minutes.
```

## Adapting Existing Content

When rewriting AI-generated content for a specific voice, work in this order:

1. **Define the target** -- persona, audience, formality level
2. **Read the original aloud** -- mark where the voice feels wrong
3. **Rewrite sentence by sentence** -- match each to the target voice
4. **Check consistency** -- run the swap test and attribution test
5. **Read aloud again** -- the final version should sound like one person wrote it

### Common Voice Drift Patterns

| Drift Pattern                       | Cause                            | Fix                                                 |
| ----------------------------------- | -------------------------------- | --------------------------------------------------- |
| Formal intro, casual body           | Different AI prompts per section | Rewrite the intro to match body tone                |
| Technical jargon spikes mid-piece   | AI pulled from technical sources | Define a jargon budget and stick to it              |
| Sudden second-person shift          | AI mixed "the user" with "you"   | Pick one perspective and apply throughout           |
| Emotional tone in a technical piece | AI added engagement phrases      | Strip hollow empathy; let facts speak               |
| Marketing language in docs          | AI conflated audiences           | Separate benefit claims from implementation details |
