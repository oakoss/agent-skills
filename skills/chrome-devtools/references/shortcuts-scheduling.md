---
title: Workflow Shortcuts and Scheduling
description: Creating reusable workflow shortcuts and scheduled recurring browser automation tasks in the Chrome extension
tags: [shortcuts, scheduling, automation, recurring-tasks, slash-commands]
---

# Workflow Shortcuts and Scheduling

These features are part of the Claude in Chrome extension (not Claude Code CLI). Shortcuts and scheduling work directly in the extension sidebar.

## Workflow Shortcuts

Shortcuts are saved prompts accessible by typing "/" in the extension chat. They allow reuse of proven workflows without retyping instructions.

### Record a Workflow

1. Click the cursor/record icon in the extension panel (or type "/" then "Record workflow")
2. Perform actions while Claude watches
3. Claude generates a shortcut with name, description, and URL

### Save from Conversation

- Click "Convert to task" on the conversation header to save a completed workflow
- Hover over a sent prompt to reveal an icon that saves it directly as a shortcut

### Edit and Manage

Edit or delete shortcuts through the extension settings.

## Scheduled Tasks

Once a workflow runs reliably, schedule it to run automatically.

### How to Schedule

1. When creating or editing a shortcut, toggle "Schedule" at the bottom
2. Set frequency: daily, weekly, monthly, or annually
3. Choose date/time and select which model to use
4. Claude runs the workflow at the specified time and notifies on completion

Alternatively, click the clock icon in the upper right corner of the extension panel to schedule shortcuts.

### Requirements

- Chrome must be open for scheduled tasks to run; if the browser is closed, the task waits until reopened
- Claude does not retain context across scheduled runs; each execution starts fresh
- Enable notifications to receive alerts when Claude requires permission or completes a task

## Shortcut Examples

### Email Management

```text
/inbox-cleanup
Archive emails from newsletters, star emails mentioning deadlines,
delete obvious spam
```

### Research

```text
/competitor-scan
Check competitor blogs, pricing pages, and careers pages.
Summarize any changes since last week.
```

### Form Filling

```text
/vendor-application
Fill vendor application form using our company documents.
Pause before final submission for review.
```

### Meeting Prep

```text
/stakeholder-map
Research LinkedIn profiles of meeting attendees.
Summarize their backgrounds and priorities.
```

### Analytics Summary

```text
/weekly-traffic
Navigate to Google Analytics, get this week's traffic summary,
and save it to a file.
```
