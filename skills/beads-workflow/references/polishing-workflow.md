---
title: Polishing Workflow
description: Iterative polishing protocol for beads, fresh session technique, cross-model review, and quality checklist
tags: [polish, review, quality, fresh-session, cross-model, checklist]
---

# Polishing Workflow

## Why Polish?

Even after initial conversion, beads continue to improve with review. Each round catches missing dependencies, oversimplified descriptions, lost features, and missing test coverage. You get incremental improvements even at round 6+.

## Polish Prompt (Full Version)

Use when you still have the original plan file available. Replace `YOUR_PLAN_FILE.md` with the actual filename.

```text
Reread AGENTS dot md so it's still fresh in your mind. Then read ALL of YOUR_PLAN_FILE.md . Use ultrathink. Check over each bead super carefully-- are you sure it makes sense? Is it optimal? Could we change anything to make the system work better for users? If so, revise the beads. It's a lot easier and faster to operate in "plan space" before we start implementing these things! DO NOT OVERSIMPLIFY THINGS! DO NOT LOSE ANY FEATURES OR FUNCTIONALITY! Also make sure that as part of the beads we include comprehensive unit tests and e2e test scripts with great, detailed logging so we can be sure that everything is working perfectly after implementation. It's critical that EVERYTHING from the markdown plan be embedded into the beads so that we never need to refer back to the markdown plan and we don't lose any important context or ideas or insights into the new features planned and why we are making them.
```

## Polish Prompt (Standard Version)

Use when beads are the primary source of truth and the plan is no longer needed.

```text
Reread AGENTS dot md so it's still fresh in your mind. Check over each bead super carefully-- are you sure it makes sense? Is it optimal? Could we change anything to make the system work better for users? If so, revise the beads. It's a lot easier and faster to operate in "plan space" before we start implementing these things!

DO NOT OVERSIMPLIFY THINGS! DO NOT LOSE ANY FEATURES OR FUNCTIONALITY!

Also, make sure that as part of these beads, we include comprehensive unit tests and e2e test scripts with great, detailed logging so we can be sure that everything is working perfectly after implementation. Remember to ONLY use the `bd` tool to create and modify the beads and to add the dependencies to beads. Use ultrathink.
```

## Polishing Protocol

1. Run the polish prompt
2. Review changes the model made
3. Repeat until steady-state (typically 6-9 rounds)
4. If progress flatlines, use the fresh session technique below
5. Optionally run a final pass with a different model

## Fresh Session Technique

When polishing starts producing diminishing returns, start a brand new session to break out of the plateau.

**Step 1 -- Re-establish context:**

```text
First read ALL of the AGENTS dot md file and README dot md file super carefully and understand ALL of both! Then use your code investigation agent mode to fully understand the code, and technical architecture and purpose of the project. Use ultrathink.
```

**Step 2 -- Review existing beads:**

```text
We recently transformed a markdown plan file into a bunch of new beads. I want you to very carefully review and analyze these using `bd` and `bv`.
```

**Step 3** -- Follow up with the standard polish prompt.

The fresh session brings a clean context window, which often catches issues that accumulated context obscured.

## Cross-Model Review

For extra polish, have different models review the beads. Each model brings a different perspective.

| Model                      | Strength                        |
| -------------------------- | ------------------------------- |
| **Claude Code + Opus 4.5** | Primary creation and refinement |
| **Codex + GPT 5.2**        | Final review pass               |
| **Gemini CLI**             | Alternative perspective         |

## When Beads Are Ready

Beads are ready for implementation when:

1. **Steady-state reached** -- Multiple polishing rounds yield minimal changes
2. **Cross-model reviewed** -- At least one alternative model has reviewed
3. **No cycles** -- `bv --robot-insights` shows no dependency cycles
4. **Tests included** -- Each feature bead has associated test beads
5. **Dependencies clean** -- The dependency graph makes logical sense

## Quality Checklist

Before handing beads off for implementation, verify each one:

- **Self-contained** -- Can be understood without external context
- **Clear scope** -- One coherent piece of work
- **Dependencies explicit** -- Links to blocking and blocked beads
- **Testable** -- Clear success criteria
- **Includes tests** -- Unit tests and e2e tests in scope
- **Preserves features** -- Nothing from the plan was lost
- **Not oversimplified** -- Complexity preserved where needed
