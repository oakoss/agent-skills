---
title: Troubleshooting and Best Practices
description: Fixing common Chrome integration issues including extension detection, browser responsiveness, connection problems, and security
tags: [troubleshooting, debugging, extension, connection, security, permissions]
---

# Troubleshooting and Best Practices

## Extension Not Detected

If Claude Code shows "Chrome extension not detected":

1. Verify the Chrome extension (v1.0.36+) is installed from Chrome Web Store
2. Verify Claude Code is v2.0.73+ by running:

```bash
claude --version
```

3. Check that Chrome is running
4. Run `/chrome` and select "Reconnect extension"
5. If the issue persists, restart both Claude Code and Chrome

## First-Time Setup Issues

On first use, Claude Code installs a native messaging host for CLI-to-Chrome communication. If permission errors occur, restart Chrome for the installation to take effect.

## Browser Not Responding

- Check for blocking modal dialogs (alert, confirm, prompt) -- these prevent Claude from receiving commands
- Ask Claude to create a new tab and retry
- Restart Chrome extension (disable/re-enable in chrome://extensions)

## Context Usage

Enabling Chrome by default (via `/chrome` > "Enabled by default") increases context consumption because browser tools are always loaded. Use the `--chrome` flag only when browser tasks are needed to reduce context usage.

## Best Practices

1. **Be specific** -- Ambiguous instructions produce inconsistent results; name exact fields, values, and actions
2. **Add verification** -- For long lists or multi-step flows, add "verify you completed all items"
3. **Handle modals** -- Dismiss JavaScript alerts, confirms, and prompts manually, then tell Claude to continue
4. **Use fresh tabs** -- If a tab becomes unresponsive, ask Claude to create a new one
5. **Filter console output** -- Specify log patterns or error types rather than requesting all console output

## Security Considerations

- Site-level permissions control which sites Claude can access
- High-risk actions (publish, purchase, share data) require user confirmation
- Some site categories are blocked (financial services, adult content)
- Manage permissions in the Chrome extension settings
- Run `/chrome` to view current permission settings

## When to Use Browser Automation

**Good for:**

- Form filling and data entry across authenticated sites
- Button clicking and multi-step navigation
- Extracting structured data from web pages
- Testing web applications (forms, flows, console errors)
- Executing predefined workflows behind logins
- Recording interactions as GIFs for documentation

**Better handled manually:**

- One-click tasks (faster by hand)
- Subjective decisions requiring human judgment
- Exploratory research (use Claude.ai chat instead)
