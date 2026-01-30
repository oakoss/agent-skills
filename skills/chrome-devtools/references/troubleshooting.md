---
title: Troubleshooting and Best Practices
description: Fixing common Chrome integration issues including extension detection, browser responsiveness, and connection problems
tags: [troubleshooting, debugging, extension, connection]
---

# Troubleshooting and Best Practices

## Extension Not Detected

```bash
claude --version  # Should be 2.0.73+
```

Then run `/chrome` and select "Reconnect extension"

## Browser Not Responding

- Check for blocking modal dialogs (alert, confirm, prompt)
- Ask Claude to create a new tab and retry
- Restart Chrome extension (disable/re-enable in chrome://extensions)

## Best Practices

1. **Be specific** - Ambiguous instructions produce inconsistent results
2. **Add verification** - For long lists, add "verify you completed all items"
3. **Handle modals** - Dismiss alerts manually, then tell Claude to continue
4. **Use fresh tabs** - If a tab becomes unresponsive, ask for a new one
5. **Filter console output** - Specify patterns vs. requesting all logs

## Security Considerations

- Site-level permissions control which sites Claude can access
- High-risk actions (publish, purchase, share data) require confirmation
- Some site categories blocked (financial services, adult content)
- Manage permissions in extension settings
