---
title: Claude Code Chrome Integration
description: Setup and usage of Claude Code with the Chrome extension for terminal-based browser control
tags: [claude-code, chrome-extension, setup, prerequisites]
---

# Claude Code Chrome Integration

## Prerequisites

- Google Chrome browser
- Claude in Chrome extension (v1.0.36+) from Chrome Web Store
- Claude Code CLI (v2.0.73+)
- Paid Claude plan (Pro, Team, Enterprise, or Max)

## Setup

Update Claude Code:

```bash
claude update
```

Start with Chrome enabled:

```bash
claude --chrome
```

Check connection status:

```text
/chrome
```

Enable Chrome by default:

```text
/chrome
# Select "Enabled by default"
```

## Browser Capabilities

**Navigation and Interaction:**

- Navigate to URLs
- Click elements (buttons, links, form fields)
- Type text into inputs
- Scroll pages
- Create and manage tabs
- Resize windows

**Information Retrieval:**

- Read page content and DOM state
- Access console logs and errors
- Monitor network requests
- Extract structured data from pages

**Advanced:**

- Fill forms automatically
- Record browser actions as GIFs
- Chain browser + terminal commands
- Work across multiple tabs

## How It Works

1. Extension uses Chrome's Native Messaging API to receive commands
2. Claude opens new tabs for tasks (does not take over existing tabs)
3. Uses your browser's login state -- no re-authentication needed
4. Pauses for CAPTCHAs, login prompts, or modal dialogs (you handle, then continue)

## Example Prompts

### Basic Navigation

```text
Go to github.com/anthropics and click on the "Code" tab
```

### Form Testing

```text
Open localhost:3000, try submitting the login form with invalid data,
and check if error messages appear correctly
```

### Console Debugging

```text
Open the dashboard page and check the console for any errors when
the page loads
```

### Data Extraction

```text
Go to the product listings page and extract the name, price, and
availability for each item. Save as CSV.
```

### Authenticated Workflows

```text
Draft a project update based on our recent commits and add it to
my Google Doc at docs.google.com/document/d/abc123
```

### Record Demo GIF

```text
Record a GIF showing the checkout flow from adding an item to cart
through to the confirmation page
```
