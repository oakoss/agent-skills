---
title: Chrome DevTools MCP Tools
description: Complete reference for the 26 Chrome DevTools MCP tools covering input, navigation, debugging, network, performance, and emulation
tags: [mcp, devtools, tools, automation, debugging]
---

# Chrome DevTools MCP Tools

## Installation

```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

Or add to MCP config:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

## Available Tools (26 total)

### Input Automation (8 tools)

- `click` - Click elements
- `drag` - Drag and drop
- `fill` - Fill input fields
- `fill_form` - Fill entire forms
- `handle_dialog` - Handle alerts/confirms/prompts
- `hover` - Hover over elements
- `press_key` - Keyboard input
- `upload_file` - Upload files

### Navigation (6 tools)

- `navigate_page` - Go to URL
- `new_page` - Create new tab
- `close_page` - Close tab
- `list_pages` - List open pages
- `select_page` - Switch to page
- `wait_for` - Wait for element/condition

### Debugging (5 tools)

- `take_screenshot` - Capture page
- `take_snapshot` - Capture DOM
- `evaluate_script` - Run JavaScript
- `get_console_message` - Get console log
- `list_console_messages` - Get all logs

### Network (2 tools)

- `list_network_requests` - List requests
- `get_network_request` - Get request details

### Performance (3 tools)

- `performance_start_trace` - Start tracing
- `performance_stop_trace` - Stop tracing
- `performance_analyze_insight` - Analyze results

### Emulation (2 tools)

- `emulate` - Emulate device
- `resize_page` - Resize viewport

## Configuration Options

```bash
# Connect to running Chrome
npx chrome-devtools-mcp@latest --browser-url http://localhost:9222

# Headless mode
npx chrome-devtools-mcp@latest --headless

# Custom viewport
npx chrome-devtools-mcp@latest --viewport 1920x1080

# Use Chrome Canary
npx chrome-devtools-mcp@latest --channel canary
```
