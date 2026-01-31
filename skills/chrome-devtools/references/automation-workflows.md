---
title: Browser Automation Workflows
description: Common browser automation patterns including testing, data extraction, email management, and multi-site research
tags: [automation, workflows, testing, data-extraction, email, multi-tab]
---

# Browser Automation Workflows

## Testing Local Development

```text
Open localhost:3000, test the new form validation, check console for errors,
and screenshot any issues you find
```

## Authenticated Data Extraction

```text
Go to my Google Analytics, get this week's traffic summary,
and save it to a file
```

## Content Management

```text
Open my Notion workspace, find the Q4 planning doc,
and add a new section with today's meeting notes
```

## Email Drafts

```text
Open Gmail, find unread emails from the engineering team,
and draft replies for each one without sending
```

## Multi-Site Research

```text
Compare pricing on our product page vs the top 3 competitors.
Create a markdown table with the differences.
```

## Form Automation

```text
I have contacts in contacts.csv. For each row, go to crm.example.com,
click "Add Contact", and fill in the name, email, and phone fields.
```

## Design Verification

```text
Build this UI from the Figma mock, then open it in the browser
and verify it matches the design
```

## Live Debugging Loop

```text
Open the dashboard page, check the console for errors on load,
then fix the code that caused them and verify the fix in the browser
```

## Multi-Tab Workflows

Claude works across tabs in the same tab group. Drag tabs into Claude's tab group for simultaneous access.

- Reference information from multiple tabs
- Copy data between tabs
- Coordinate actions across sites

## When to Use Browser Automation

**Good for:**

- Form filling and data entry
- Button clicking and navigation
- Extracting data from authenticated pages
- Testing web applications
- Executing predefined workflows
- Tasks behind logins

**Better manually:**

- One-click tasks (faster by hand)
- Subjective decisions
- Exploratory research (use Claude.ai chat instead)

## Tips

1. **Be specific** -- Ambiguous instructions produce inconsistent results
2. **Add verification** -- For long lists, add "verify you completed all items"
3. **Handle modals** -- Dismiss alerts manually, then tell Claude to continue
4. **Use fresh tabs** -- If a tab becomes unresponsive, ask for a new one
5. **Filter console output** -- Specify patterns instead of requesting all logs
6. **Chain browser + terminal** -- Claude can scrape a site, analyze the data, generate code, and commit in one workflow

## Security

- Site-level permissions control which sites Claude can access
- High-risk actions (publish, purchase, share data) require confirmation
- Some site categories blocked (financial services, adult content)
- Manage permissions in extension settings
