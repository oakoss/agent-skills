---
title: Claude Code Chrome Integration
description: Setup and usage of Claude Code with the Chrome extension for terminal-based browser control
tags: [claude-code, chrome-extension, setup, prerequisites, native-messaging]
---

# Claude Code Chrome Integration

## Prerequisites

- Google Chrome browser (latest stable)
- Claude in Chrome extension (v1.0.36+) from Chrome Web Store
- Claude Code CLI (v2.0.73+)
- Paid Claude plan (Pro, Team, or Enterprise)

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

Enable Chrome by default (increases context usage since browser tools are always loaded):

```text
/chrome
# Select "Enabled by default"
```

On first use, Claude Code installs a native messaging host that allows communication between the CLI and Chrome. Restart Chrome if permission errors occur.

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
- Record browser interactions as GIFs
- Chain browser + terminal commands in a single workflow
- Work across multiple tabs

## How It Works

1. Extension uses Chrome's Native Messaging API to receive commands from Claude Code
2. Claude opens new tabs for tasks (does not take over existing tabs)
3. Uses the browser's login state -- no re-authentication needed
4. Pauses for CAPTCHAs, login prompts, or modal dialogs (user handles, then continues)
5. Requires a visible browser window; no headless mode for the extension path

Run `/mcp` and click into `claude-in-chrome` to see the full list of available tools.

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

### Design Verification

```text
Build this UI from the Figma mock, then open it in the browser and
verify it matches the design
```

### Multi-Site Workflow

```text
Check my calendar for meetings tomorrow, then for each meeting with
an external attendee, look up their company on LinkedIn and add a
note about what they do
```
