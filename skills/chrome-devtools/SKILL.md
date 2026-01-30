---
name: chrome-devtools
description: 'Browser automation via Chrome extension. Use when controlling a logged-in Chrome browser, automating workflows, filling forms, extracting data, or running scheduled browser tasks.'
---

# Claude in Chrome Skill

Control your real Chrome browser with Claude. The extension runs in your authenticated browser session, so Claude can interact with sites you are already logged into -- Gmail, Google Docs, Notion, CRMs, and more.

## Overview

There are two integration options: Claude Code + Chrome Extension (terminal-based via `claude --chrome`) and Chrome DevTools MCP (26 browser automation tools via Model Context Protocol). Both use your real Chrome with existing logins.

## Quick Reference

| Integration             | Setup                                                           | Best For                              |
| ----------------------- | --------------------------------------------------------------- | ------------------------------------- |
| Claude Code + Extension | `claude --chrome`                                               | Terminal-based browser control        |
| Chrome DevTools MCP     | `claude mcp add chrome-devtools npx chrome-devtools-mcp@latest` | Programmatic automation via MCP tools |

| Capability | Tools/Methods                                                        |
| ---------- | -------------------------------------------------------------------- |
| Navigation | Navigate URLs, create/close/switch tabs, resize windows              |
| Input      | Click, type, fill forms, drag, hover, press keys, upload files       |
| Extraction | Read page content, DOM state, console logs, network requests         |
| Debugging  | Screenshots, DOM snapshots, evaluate JavaScript, performance tracing |
| Emulation  | Device emulation, viewport resizing                                  |
| Scheduling | Workflow shortcuts with daily/weekly/monthly triggers                |

| Requirement                | Minimum                       |
| -------------------------- | ----------------------------- |
| Google Chrome              | Latest stable                 |
| Claude in Chrome Extension | 1.0.36+                       |
| Claude Code CLI            | 2.0.73+                       |
| Claude Plan                | Pro, Team, Enterprise, or Max |
| Node.js (DevTools MCP)     | 20.19+                        |

**Not supported**: Other Chromium browsers (Brave, Arc, Edge), WSL, headless mode (extension only), mobile devices.

## Common Mistakes

| Mistake                                            | Correct Pattern                                                                                          |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Running browser automation without `--chrome` flag | Start Claude Code with `claude --chrome` or enable Chrome by default via `/chrome` settings              |
| Trying to take over existing tabs                  | Claude opens new tabs for tasks; it does not hijack tabs you already have open                           |
| Not handling CAPTCHAs and modal dialogs manually   | Claude pauses at CAPTCHAs, login prompts, and modals; dismiss them yourself then tell Claude to continue |
| Using ambiguous instructions for form filling      | Be specific about field names, values, and order; ambiguous prompts produce inconsistent results         |
| Requesting all console logs without filtering      | Specify log patterns or error types; requesting everything floods context with noise                     |

## Delegation

- **Automate repetitive browser workflows across sites**: Use `Task` agent with Chrome extension to fill forms, extract data, or navigate multi-step flows
- **Debug frontend issues with console and network inspection**: Use `Explore` agent with DevTools MCP to capture console errors, network failures, and DOM state
- **Plan complex multi-tab data extraction pipelines**: Use `Plan` agent to design the workflow steps before executing browser automation

## References

- [Claude Code Chrome integration](references/claude-code-integration.md)
- [Chrome DevTools MCP tools](references/devtools-mcp.md)
- [Browser automation workflows](references/automation-workflows.md)
- [Workflow shortcuts and scheduling](references/shortcuts-scheduling.md)
- [Troubleshooting and best practices](references/troubleshooting.md)
