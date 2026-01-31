---
title: Review Workflow
description: Prompts, checklists, and integration patterns for systematically de-slopifying documentation and code
tags: [workflow, prompts, checklist, integration, automation, review, scanning]
---

# Review Workflow

## The Core Prompt

Use this prompt to trigger a full de-slopify pass on any document. The key instruction is manual, line-by-line review; no regex or automated substitution.

```text
Read through the complete text carefully and look for any telltale signs of
"AI slop" style writing; one big tell is the use of emdash. Replace with a
semicolon, a comma, or recast the sentence so it sounds good while avoiding
emdash.

Also avoid certain telltale writing tropes, like sentences of the form
"It's not [just] XYZ, it's ABC" or "Here's why" or "Here's why it matters:".
Basically, anything that sounds like the kind of thing an LLM would write
disproportionately more commonly than a human writer and which sounds
inauthentic/cringe.

You MUST manually read each line of the text and revise it in a systematic,
methodical, diligent way. Use ultrathink.
```

## Quick Prompt (Minor Touch-Ups)

For documents that are mostly clean but need a light pass:

```text
Review this text and remove AI slop patterns: excessive emdashes, "Here's why"
constructions, "It's not X, it's Y" formulas, and other LLM writing tells.
Recast sentences to sound naturally human. Use ultrathink.
```

## Code Review Prompt

For AI-generated code:

```text
Review this code for AI-generated patterns: over-commenting (comments that
restate the code), unnecessary abstractions (interfaces with one implementation,
factories for simple construction), verbose variable names, defensive error
handling that adds no value (try-catch that logs and re-throws, null checks
on non-nullable types), and duplicated logic. Simplify to the minimal working
solution. Use ultrathink.
```

## Pre-Edit Checklist

Before starting any de-slopify pass, answer these questions:

| Question                            | Why It Matters                                        |
| ----------------------------------- | ----------------------------------------------------- |
| Who is the author persona?          | A maintainer writes differently than a marketing team |
| What tone?                          | Conversational, professional, terse, friendly         |
| Who reads this?                     | Engineers, end users, or stakeholders                 |
| What is the publication context?    | README, API docs, blog post, changelog                |
| Is technical accuracy the priority? | Never sacrifice correctness for style                 |

## The Review Process

### Step 1: Scan for Density

Run a quick grep to estimate slop density:

```bash
grep -icE "delve|tapestry|landscape|revolutionize|leverage|seamless|game.changer|worth noting|at its core|in essence|here's why|dive in|ever-evolving|furthermore|moreover" README.md
```

Use the count to decide the scope of review:

| Matches per 500 words | Scope                                     |
| --------------------- | ----------------------------------------- |
| 0-2                   | Spot fixes only                           |
| 3-5                   | Section-level rewrite                     |
| 6-10                  | Full document rewrite                     |
| 11+                   | Start from scratch or use the full prompt |

### Step 2: Define Voice

Set the persona, tone, and audience before editing. Write a one-sentence voice description:

```text
Voice: Senior engineer writing for other engineers. Direct, specific, no
hedging. Uses contractions. Cites exact versions and error codes.
```

### Step 3: Line-by-Line Review

Work through the document section by section:

1. Read each sentence aloud (mentally or actually)
2. Flag emdashes, slop phrases, and vocabulary tells
3. For each flag, choose: delete, replace, or recast the sentence
4. Check that the fix maintains the surrounding paragraph's flow
5. Verify no technical accuracy was lost

### Step 4: Rhythm Check

After individual fixes, read full paragraphs for rhythm:

- Are sentences varied in length?
- Do any paragraphs feel metronomic?
- Is there at least one short, punchy sentence per section?
- Are lists varied in item count (not always exactly three)?

### Step 5: Read-Aloud Test

Read the final text aloud. If any sentence makes you cringe or sounds like a chatbot wrote it, it needs another pass.

## When to De-Slopify

| Trigger                                     | Scope                                  |
| ------------------------------------------- | -------------------------------------- |
| Before publishing a README                  | Full document review                   |
| Before releasing documentation              | Full review of changed files           |
| After an AI-assisted writing session        | Review all generated sections          |
| During documentation review / PR review     | Review the diff only                   |
| Before committing prose that an LLM touched | Quick pass on changed lines            |
| After multiple iterative AI code edits      | Code slop review of affected functions |

## Files to Prioritize

Focus on public-facing text first:

1. README.md
2. CONTRIBUTING.md
3. API documentation
4. Blog posts and announcements
5. Changelog entries
6. Error messages and user-facing strings
7. CLI help text

Code comments are lower priority; they follow the project's comment policy.

## Integration with Git Workflow

### As a Pre-Commit Check

Add a slop scan to your review process. This is not a blocker; it identifies candidates for human review.

```bash
# In a CI script or pre-commit hook, flag files with high slop density
for file in $(git diff --cached --name-only --diff-filter=AM -- '*.md'); do
  count=$(grep -icE "delve|tapestry|landscape|revolutionize|leverage|seamless|worth noting|at its core|here's why|dive in|ever-evolving" "$file" || true)
  if [ "$count" -gt 5 ]; then
    echo "WARNING: $file has $count potential slop markers. Review before publishing."
  fi
done
```

### As a PR Review Step

When reviewing a PR that includes documentation changes:

1. Check the diff for slop vocabulary clusters
2. Flag sections that read as unedited LLM output
3. Request rewrites with a specific voice direction, not just "fix the AI slop"

### As a Periodic Audit

Run a repository-wide scan quarterly:

```bash
# Scan all markdown files and sort by slop density
for file in $(find . -name "*.md" -not -path "./node_modules/*"); do
  count=$(grep -icE "delve|tapestry|landscape|revolutionize|leverage|seamless|worth noting|at its core|here's why|dive in|ever-evolving" "$file" || true)
  if [ "$count" -gt 0 ]; then
    echo "$count $file"
  fi
done | sort -rn
```

## Troubleshooting

### "I fixed the emdashes but it still sounds AI-generated"

Emdashes are the most visible tell but not the only one. Check for uniform sentence length, generic claims, and formulaic structures. Vary rhythm and inject specific details: names, dates, numbers, version strings.

### "The text sounds choppy after edits"

Over-correction. Read the text aloud. Some sentences need combining or transitional words. Not every emdash needs replacing; use judgment about which ones sound natural.

### "How do I know when I'm done?"

The read-aloud test. If a competent developer can read the document without thinking "AI wrote this," you are done.

### "Should I de-slopify code comments too?"

Focus on public-facing prose first. Code comments follow the project's comment policy. Over-commented AI code is a separate problem (see the code slop reference) that should be addressed during code review, not during a prose de-slopify pass.

### "The AI keeps re-adding slop when I ask it to edit"

Be explicit in your prompt about what to avoid. Include the slop vocabulary list. Use the full prompt from this reference, not a vague instruction like "make it sound human." The "Use ultrathink" instruction forces deeper reasoning about each sentence.
