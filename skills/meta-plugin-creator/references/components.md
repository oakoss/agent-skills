---
title: Plugin Components
description: Skills, agents, commands, hooks, MCP servers, and LSP servers bundled in plugins
tags: [skills, agents, commands, hooks, mcp-servers, lsp-servers, components]
---

# Plugin Components

## Skills

Skills are auto-discovered from `skills/*/SKILL.md` and provide context-aware capabilities that the agent loads when relevant.

```sh
skills/
└── code-review/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

Each `SKILL.md` needs frontmatter with `name` and `description`:

```yaml
---
name: code-review
description: Reviews code for best practices and potential issues. Use when reviewing code, checking PRs, or analyzing code quality.
---

When reviewing code, check for:
1. Code organization and structure
2. Error handling
3. Security concerns
4. Test coverage
```

Skills support the full Agent Skills standard including reference files, scripts, and progressive disclosure.

## Commands

Commands are slash commands defined as Markdown files in `commands/`. They are namespaced by plugin name: a command at `commands/deploy.md` in a plugin named `my-tools` is invoked as `/my-tools:deploy`.

```markdown
---
description: Deploy to production
argument-hint: [environment]
---

Deploy the application to $ARGUMENTS environment.
```

| Frontmatter Field | Required | Description                       |
| ----------------- | -------- | --------------------------------- |
| `description`     | Yes      | Shown in `/help` and autocomplete |
| `argument-hint`   | No       | Hint text for autocomplete        |

The `$ARGUMENTS` placeholder captures any text the user provides after the command name.

## Agents

Agents are specialized subagents defined as Markdown files in `agents/`. They appear in the `/agents` interface and can be invoked automatically based on task context.

```markdown
---
description: Review code for security vulnerabilities
capabilities: ['security-analysis', 'vulnerability-detection']
tools: Read, Grep, Glob
model: haiku
---

# Security Reviewer

You review code for security issues. Focus on:

- Authentication and authorization flaws
- Input validation gaps
- Injection vulnerabilities
- Sensitive data exposure
```

| Frontmatter Field | Required | Description                   |
| ----------------- | -------- | ----------------------------- |
| `description`     | Yes      | What the agent specializes in |
| `capabilities`    | No       | List of task categories       |
| `tools`           | No       | Allowed tools for the agent   |
| `model`           | No       | Model to use (e.g., `haiku`)  |

## Hooks

Hooks are event handlers that run automatically when specific events occur. Define them in `hooks/hooks.json` or inline in `plugin.json`.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format.sh"
          }
        ]
      }
    ]
  }
}
```

### Available Events

| Event                | Trigger                                  |
| -------------------- | ---------------------------------------- |
| `PreToolUse`         | Before any tool execution                |
| `PostToolUse`        | After successful tool execution          |
| `PostToolUseFailure` | After tool execution fails               |
| `PermissionRequest`  | When a permission dialog is shown        |
| `UserPromptSubmit`   | When user submits a prompt               |
| `Notification`       | When a notification is sent              |
| `Stop`               | When the agent attempts to stop          |
| `SubagentStart`      | When a subagent is started               |
| `SubagentStop`       | When a subagent attempts to stop         |
| `SessionStart`       | At the beginning of sessions             |
| `SessionEnd`         | At the end of sessions                   |
| `PreCompact`         | Before conversation history is compacted |

### Hook Types

| Type      | Description                                          |
| --------- | ---------------------------------------------------- |
| `command` | Execute shell commands or scripts                    |
| `prompt`  | Evaluate a prompt with an LLM (uses `$ARGUMENTS`)    |
| `agent`   | Run an agentic verifier with tools for complex tasks |

Event names are case-sensitive. Scripts must be executable (`chmod +x`).

## MCP Servers

MCP servers connect the plugin to external tools via the Model Context Protocol. Define them in `.mcp.json` or inline in `plugin.json`.

```json
{
  "mcpServers": {
    "plugin-database": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_PATH": "${CLAUDE_PLUGIN_ROOT}/data"
      }
    },
    "plugin-api": {
      "command": "npx",
      "args": ["@company/mcp-server", "--plugin-mode"],
      "cwd": "${CLAUDE_PLUGIN_ROOT}"
    }
  }
}
```

Plugin MCP servers start automatically when the plugin is enabled and appear as standard tools in the agent toolkit.

## LSP Servers

LSP servers provide real-time code intelligence (diagnostics, go-to-definition, find references). Define them in `.lsp.json` or inline in `plugin.json`.

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

### Required LSP Fields

| Field                 | Description                                  |
| --------------------- | -------------------------------------------- |
| `command`             | LSP binary to execute (must be in PATH)      |
| `extensionToLanguage` | Maps file extensions to language identifiers |

### Optional LSP Fields

| Field                   | Description                                     |
| ----------------------- | ----------------------------------------------- |
| `args`                  | Command-line arguments                          |
| `transport`             | `stdio` (default) or `socket`                   |
| `env`                   | Environment variables for the server            |
| `initializationOptions` | Options passed during initialization            |
| `settings`              | Settings via `workspace/didChangeConfiguration` |
| `workspaceFolder`       | Workspace folder path                           |
| `startupTimeout`        | Max startup wait time (ms)                      |
| `shutdownTimeout`       | Max graceful shutdown wait time (ms)            |
| `restartOnCrash`        | Auto-restart on crash                           |
| `maxRestarts`           | Maximum restart attempts                        |
| `loggingConfig`         | Debug logging configuration                     |

### TypeScript LSP Example

Complete configuration showing initializationOptions and logging:

```json
{
  "typescript": {
    "command": "typescript-language-server",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".ts": "typescript",
      ".tsx": "typescriptreact",
      ".js": "javascript",
      ".jsx": "javascriptreact"
    },
    "initializationOptions": {
      "preferences": {
        "includeInlayParameterNameHints": "all"
      }
    },
    "loggingConfig": {
      "args": ["--log-level", "verbose"],
      "env": {
        "TSS_LOG": "-level verbose -file ${CLAUDE_PLUGIN_LSP_LOG_FILE}"
      }
    }
  }
}
```

The language server binary must be installed separately. The plugin configures how the agent connects to it.
