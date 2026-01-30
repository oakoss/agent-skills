---
name: de-slopify
description: 'Removes AI writing artifacts from documentation. Use when editing LLM-generated prose, reviewing READMEs, or polishing docs before publishing. Use for emdash cleanup, formulaic phrase removal, and tone calibration.'
---

# De-Slopify -- Remove AI Writing Artifacts

> **Purpose:** Make documentation sound like it was written by a human, not an LLM.
>
> **Key Insight:** You cannot do this with regex or a script. It requires manual, line-by-line review with judgment about context, tone, and intent.

---

## Quick Reference

### The Prompt

```text
Read through the complete text carefully and look for any telltale signs of "AI slop" style writing; one big tell is the use of emdash. Replace with a semicolon, a comma, or recast the sentence so it sounds good while avoiding emdash.

Also avoid certain telltale writing tropes, like sentences of the form "It's not [just] XYZ, it's ABC" or "Here's why" or "Here's why it matters:". Basically, anything that sounds like the kind of thing an LLM would write disproportionately more commonly than a human writer and which sounds inauthentic/cringe.

You MUST manually read each line of the text and revise it in a systematic, methodical, diligent way. Use ultrathink.
```

### Quick Version (minor touch-ups)

```text
Review this text and remove AI slop patterns: excessive emdashes, "Here's why" constructions, "It's not X, it's Y" formulas, and other LLM writing tells. Recast sentences to sound naturally human. Use ultrathink.
```

---

## Core Patterns

### What Counts as "AI Slop"

AI slop refers to writing patterns that LLMs produce disproportionately more often than human writers. These patterns make text feel inauthentic.

| Pattern                                            | Problem                                                                  |
| -------------------------------------------------- | ------------------------------------------------------------------------ |
| Emdash overuse                                     | LLMs chain emdashes constantly, even when other punctuation works better |
| "It's not X, it's Y"                               | Formulaic contrast structure                                             |
| "Here's why" / "Here's why it matters:"            | Clickbait-style lead-in                                                  |
| "Let's dive in" / "Let's get started"              | Forced enthusiasm                                                        |
| "In this guide, we'll..."                          | Overly formal setup                                                      |
| "It's worth noting that..."                        | Unnecessary hedge                                                        |
| "At its core..." / "In essence..."                 | Pseudo-profound opener                                                   |
| "Revolutionize" / "In the ever-evolving landscape" | High-confidence AI markers                                               |
| "In conclusion" / "To summarize"                   | Robotic closers                                                          |
| Uniform sentence length                            | Machine-like rhythm; humans vary between short and long                  |
| Perfectly balanced lists of 3                      | Humans often use 2 or 4, or add an outlier                               |
| Generic claims without specifics                   | Lacks the first-person experience that signals real expertise            |

### Emdash Alternatives

When you encounter an emdash, consider these replacements:

| Original                                  | Alternative                                       |
| ----------------------------------------- | ------------------------------------------------- |
| `X--Y--Z`                                 | `X; Y; Z` or `X, Y, Z`                            |
| `The tool--which is powerful--works well` | `The tool, which is powerful, works well`         |
| `We built this--and it works`             | `We built this, and it works`                     |
| `Here's the thing--it matters`            | `Here's the thing: it matters` or recast entirely |

Sometimes the best fix is splitting into two sentences or restructuring entirely.

### Phrase Replacement Guide

**"Here's why" family:**

- "Here's why" -- Just explain why directly
- "Here's why it matters" -- Explain the importance inline
- "Here's the thing" -- Usually can be deleted entirely

**Contrast formulas:**

- "It's not X, it's Y" -- "This is Y" or explain the distinction differently
- "It's not just X, it's also Y" -- "This does X and Y"

**Forced enthusiasm:**

- "Let's dive in!" -- Just start
- "Excited to share..." -- Just share it

**Pseudo-profound openers:**

- "At its core..." -- Usually deletable
- "Fundamentally..." -- Often unnecessary
- "In essence..." -- Just say the essence

**Unnecessary hedges:**

- "It's worth noting that..." -- Just note it
- "It's important to remember..." -- Just state the fact
- "Keep in mind that..." -- Often deletable

**Robotic closers:**

- "In conclusion" -- Use "The Bottom Line" or "What this means for you", or nothing
- "To summarize" -- Same treatment

### Linguistic Pattern Breaking

Humans write with varied rhythm. AI tends toward uniform sentence length and predictable structure.

- Mix short punchy sentences (5 words) with longer exploratory ones (20+ words)
- Avoid perfectly parallel list items; add an outlier or vary structure
- Use contractions where natural ("don't", "we're", "it's")
- Inject specific details: names, dates, numbers, brand references

### Voice Calibration

Before editing, define the target:

1. **Persona** -- Who is writing this? (maintainer, team lead, individual contributor)
2. **Tone** -- Conversational, professional, or direct?
3. **Audience** -- Fellow developers, end users, stakeholders?

Then maintain that voice consistently throughout.

---

## Anti-Patterns

### What NOT to Do

1. **DO NOT** sacrifice technical accuracy for style. Correctness always wins.
2. **DO NOT** remove necessary structure (headers, lists, code examples). Focus on prose.
3. **DO NOT** use "Revolutionize", "Dive into", or "In the ever-evolving landscape".
4. **DO NOT** use perfectly balanced lists of 3 every time.
5. **DO NOT** use generic claims. Replace with specific examples, data, or first-person experience.
6. **DO NOT** hide personality. If the voice is blunt, keep it blunt.
7. **DO NOT** apply fixes mechanically. Context matters; sometimes an emdash is the right choice.

### What NOT to Fix

- **Technical accuracy** -- Never sacrifice correctness for style
- **Necessary structure** -- Headers, lists, tables are fine
- **Clear explanations** -- Being thorough is not slop
- **Code examples** -- Focus on prose, not code blocks

---

## Before and After Examples

### Emdash Overuse

**Before:**

```text
This tool--which we built from scratch--handles everything automatically--from parsing to output.
```

**After:**

```text
This tool handles everything automatically, from parsing to output. We built it from scratch.
```

### "Here's Why" Pattern

**Before:**

```text
We chose Rust for this component. Here's why: performance matters, and Rust delivers.
```

**After:**

```text
We chose Rust for this component because performance matters.
```

### Contrast Formula

**Before:**

```text
It's not just a linter; it's a complete code quality system.
```

**After:**

```text
This complete code quality system goes beyond basic linting.
```

### Forced Enthusiasm

**Before:**

```markdown
# Getting Started

Let's dive in! We're excited to help you get up and running with our amazing tool.
```

**After:**

```markdown
# Getting Started

Install the tool and run your first command in under a minute.
```

### Robotic vs. Authentic

**Before:**

```text
Artificial intelligence is revolutionizing the way we write code. It provides efficiency and reduces the time required for development tasks. However, it is important to maintain quality.
```

**After:**

```text
Raw AI code is often a mess of predictable patterns and dropped context. Speed is a trap if you are not auditing for intent.
```

---

## Common Mistakes

| Mistake                                            | Correct Pattern                                                                    |
| -------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Replacing every emdash mechanically                | Evaluate context; sometimes an emdash is the right punctuation choice              |
| Editing code blocks for style                      | Focus on prose only; leave code examples, comments, and technical syntax untouched |
| Removing all structure to sound casual             | Keep headers, tables, and lists intact; only rewrite prose sections                |
| Over-correcting into choppy fragments              | Read aloud after editing and recombine sentences that lost their flow              |
| Applying fixes without defining target voice first | Set persona, tone, and audience before starting any edits                          |

## Delegation

- **Scan a repository for documentation files that need de-slopifying**: Use `Explore` agent
- **Rewrite an entire documentation site to remove AI artifacts**: Use `Task` agent
- **Plan a documentation voice guide and editorial workflow**: Use `Plan` agent

## Troubleshooting

### "I fixed the emdashes but it still sounds AI-generated"

Emdashes are the most obvious tell, but not the only one. Check for uniform sentence length, generic claims, and formulaic structures ("It's not X, it's Y"). Vary your rhythm and inject specifics.

### "The text sounds choppy after edits"

You may have over-corrected. Read the text aloud. If it does not flow, some sentences need combining or transitional phrases. Not every emdash needs replacing; use judgment.

### "How do I know when I'm done?"

Do a read-aloud test. If any sentence makes you cringe or sounds like a chatbot wrote it, keep editing. A competent developer should be able to read it without thinking "AI wrote this."

### "Should I de-slopify code comments too?"

Focus on public-facing prose: READMEs, documentation, blog posts, CONTRIBUTING guides, and API docs. Code comments follow separate rules (see comment policy).

### When to De-Slopify

- Before publishing a README
- Before releasing documentation
- After AI-assisted writing sessions
- During documentation reviews
- As a final pass before commit
