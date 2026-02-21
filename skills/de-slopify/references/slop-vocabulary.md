---
title: AI Slop Vocabulary
description: Words, phrases, and trigrams that appear disproportionately in LLM-generated text, with severity ratings and replacement guidance
tags:
  [
    vocabulary,
    words,
    phrases,
    detection,
    slop-score,
    antislop,
    trigrams,
    GPT-isms,
  ]
---

# AI Slop Vocabulary

## How Slop Vocabulary Works

Certain words and phrases appear far more frequently in LLM output than in human writing. The Antislop research project found that some patterns appear over 1,000x more frequently in AI text. The EQ-bench Slop Score weights detection as 60% individual slop words, 25% contrast patterns ("not X, but Y"), and 15% slop trigrams.

These lists are not blocklists. Every word below appears in legitimate human writing. The signal is frequency and context: "delve" in a single blog post is fine; "delve" in every other paragraph is a tell.

## High-Confidence Slop Words

These words are statistically overrepresented in LLM output across multiple models and prompt types. Seeing several in one document is a strong signal.

| Word          | Why It Flags                                            | Replacement Strategy                                             |
| ------------- | ------------------------------------------------------- | ---------------------------------------------------------------- |
| delve         | Rarely used in casual writing; LLMs default to it       | "explore", "examine", "dig into", or delete                      |
| tapestry      | Metaphor LLMs overuse for complexity                    | Use a specific metaphor or describe the actual complexity        |
| landscape     | "The ever-evolving landscape of X"                      | Delete the phrase; name the specific changes                     |
| nuanced       | Vague intensifier that adds nothing                     | Describe the specific nuance                                     |
| multifaceted  | Same problem as "nuanced"                               | Name the specific facets                                         |
| pivotal       | Overused for emphasis                                   | "important", "critical", or explain why it matters               |
| crucial       | Less flagged than "pivotal" but still overused          | "required", "necessary", or state the consequence of skipping it |
| foster        | "Foster collaboration/innovation/growth"                | "encourage", "build", "create", or delete                        |
| leverage      | Business-speak LLMs love                                | "use"                                                            |
| streamline    | Vague efficiency claim                                  | State the specific improvement                                   |
| paradigm      | Almost never used naturally in technical writing        | Delete or describe the actual shift                              |
| holistic      | Vague; rarely means anything specific                   | Name what's included                                             |
| robust        | Every LLM-generated description is "robust"             | "reliable", "tested", or describe what makes it robust           |
| comprehensive | Same as "robust"                                        | "complete", "full", or list what's covered                       |
| seamless      | Nothing is seamless; describe the actual integration    | "automatic", "zero-config", or describe what the user does       |
| revolutionize | Extreme claim LLMs make casually                        | Delete or make a specific, defensible claim                      |
| cutting-edge  | Meaningless superlative                                 | Name the specific technology or technique                        |
| game-changer  | Same as "cutting-edge"                                  | State the measurable improvement                                 |
| empower       | "Empower developers to..."                              | "lets developers..." or "developers can..."                      |
| elevate       | "Elevate your workflow"                                 | Delete; describe what changes                                    |
| resonate      | "This resonates with developers"                        | Delete or explain why specifically                               |
| moreover      | LLMs chain paragraphs with "moreover" and "furthermore" | Delete or use "also"                                             |
| furthermore   | Same as "moreover"                                      | Delete, "also", or just start the next sentence                  |
| nevertheless  | Formal transition LLMs overuse                          | "but", "still", or restructure                                   |
| harnessing    | "Harnessing the power of X"                             | "using X"                                                        |
| underscore    | "This underscores the importance of..."                 | State the importance directly                                    |
| realm         | "In the realm of X"                                     | "in X"                                                           |
| myriad        | "A myriad of options"                                   | "many options" or list them                                      |
| intricate     | Vague complexity claim                                  | Name what makes it complex                                       |
| captivating   | Rarely appropriate in technical writing                 | Delete                                                           |
| testament     | "A testament to X"                                      | Delete; just describe X                                          |
| embark        | "Embark on a journey"                                   | Delete                                                           |
| bespoke       | Overused for "custom"                                   | "custom"                                                         |
| unwavering    | "Unwavering commitment to quality"                      | Delete the whole phrase                                          |

## High-Confidence Slop Phrases

| Phrase                                 | Replacement                                |
| -------------------------------------- | ------------------------------------------ |
| "In the ever-evolving landscape of..." | Delete entirely; name the specific change  |
| "It's not just X, it's Y"              | "This is Y" or restate without the formula |
| "Here's why" / "Here's why it matters" | Explain why directly                       |
| "Let's dive in" / "Let's explore"      | Delete; start the content                  |
| "It's worth noting that"               | Delete; state the fact                     |
| "At its core" / "In essence"           | Delete; make the point                     |
| "In today's fast-paced world"          | Delete entirely                            |
| "As we navigate the complexities of"   | Delete entirely                            |
| "A testament to"                       | Delete; describe the thing directly        |
| "The power of"                         | "Using X" or delete                        |
| "Stands as a beacon of"                | Delete                                     |
| "In an era where"                      | Delete                                     |
| "Serves as a cornerstone"              | "is central to" or "is required for"       |

## Slop Trigrams

Three-word sequences that appear unnaturally often in LLM output. These are subtler than single words but accumulate into an AI feel.

| Trigram           | Context                           |
| ----------------- | --------------------------------- |
| "a testament to"  | Almost always deletable           |
| "a tapestry of"   | Replace with specific description |
| "it is important" | Rewrite as direct statement       |
| "it is worth"     | Delete the hedge                  |
| "in the realm"    | Replace with "in"                 |
| "the power of"    | Delete or be specific             |
| "serves as a"     | Replace with "is"                 |
| "in order to"     | Replace with "to"                 |
| "whether it is"   | Often deletable filler            |
| "the fact that"   | Usually deletable                 |
| "plays a crucial" | Replace with specific verb        |
| "it is essential" | State what happens if you skip it |

## Newer Model Patterns

These patterns are less about individual word choice and more about conversational habits baked into RLHF-tuned models. They survive prompt engineering and show up even when vocabulary-level slop is absent.

### Sycophancy

Models reflexively validate the user before answering. The praise is content-free and delays the actual response.

| Pattern                                  | Fix                                         |
| ---------------------------------------- | ------------------------------------------- |
| "Great question!"                        | Delete; answer directly                     |
| "Absolutely!" / "Exactly!"               | Delete or replace with the actual agreement |
| "That's a really insightful observation" | Delete; engage with the observation         |
| "You're right to be concerned about..."  | State the concern and address it            |

### False Epistemic Humility

Models hedge with faux-modesty that sounds cautious but says nothing.

| Pattern                           | Fix                                        |
| --------------------------------- | ------------------------------------------ |
| "I think it's fair to say..."     | Say it                                     |
| "It could be argued that..."      | Argue it or attribute it                   |
| "While I'm not an expert in X..." | Delete; state what you know                |
| "This is a complex topic, but..." | Delete the throat-clearing; make the point |

### Meta-Commentary

Models narrate their own reasoning process instead of just reasoning.

| Pattern                                      | Fix                         |
| -------------------------------------------- | --------------------------- |
| "Let me break this down..."                  | Delete; just break it down  |
| "Let me think about this step by step"       | Delete; show the steps      |
| "To answer your question..."                 | Delete; answer the question |
| "There are several factors to consider here" | Delete; list the factors    |

### Structured Overclarification

Models impose heavy structure on content that reads better as prose. Numbered lists, bold labels, and sub-headers appear where a single sentence would suffice.

| Signal                                       | Fix                                            |
| -------------------------------------------- | ---------------------------------------------- |
| Numbered list with 2 trivial items           | Rewrite as a sentence                          |
| Bold-labeled list restating a simple idea    | Collapse to one sentence                       |
| Nested sub-headers for a single paragraph    | Remove the sub-header; let the paragraph stand |
| "Here are the key considerations: 1. ... 2." | State the considerations in running prose      |

## Using These Lists

### For Manual Review

Scan the document for clusters of slop vocabulary. One or two flagged words in a long document means nothing. Five or more in a single section means the section needs a rewrite, not word-for-word substitution.

### For Automated Scanning

```bash
# Quick grep scan for high-confidence slop words in a file
grep -iEn "delve|tapestry|landscape|revolutionize|leverage|seamless|game.changer|cutting.edge|embark|paradigm|holistic" README.md
```

```bash
# Scan for common slop phrases
grep -iEn "ever-evolving|worth noting|at its core|in essence|here's why|dive in|let's explore|fast-paced" README.md
```

These scans identify candidates for review. Every match needs human judgment about whether the usage is natural in context.

### Severity Assessment

Count slop markers per 500 words of prose:

| Count | Assessment    | Action                            |
| ----- | ------------- | --------------------------------- |
| 0-2   | Clean         | No action needed                  |
| 3-5   | Light slop    | Targeted phrase replacement       |
| 6-10  | Moderate slop | Section-level rewrite             |
| 11+   | Heavy slop    | Full document rewrite recommended |
