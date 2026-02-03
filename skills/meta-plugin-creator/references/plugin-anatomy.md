---
title: Plugin Anatomy
description: Plugin manifest schema, directory structure, component paths, and path behavior rules
tags: [plugin.json, manifest, schema, directory-structure, component-paths]
---

# Plugin Anatomy

## Directory Structure

A complete plugin follows this layout. Only `.claude-plugin/plugin.json` is required; all other directories are optional.

```sh
my-plugin/
├── .claude-plugin/           # Metadata directory
│   └── plugin.json          # Required: plugin manifest
├── skills/                   # Agent Skills (auto-discovered)
│   └── code-review/
│       ├── SKILL.md
│       └── scripts/
├── commands/                 # Slash commands (auto-discovered)
│   ├── deploy.md
│   └── status.md
├── agents/                   # Subagents (auto-discovered)
│   ├── reviewer.md
│   └── tester.md
├── hooks/                    # Event hooks
│   └── hooks.json
├── .mcp.json                # MCP server config
├── .lsp.json                # LSP server config
├── scripts/                 # Utility scripts for hooks
│   └── format.sh
├── LICENSE
└── CHANGELOG.md
```

Only `plugin.json` belongs inside `.claude-plugin/`. All component directories (skills, commands, agents, hooks) go at the plugin root.

## Plugin Manifest Schema

### Minimal Manifest

```json
{
  "name": "my-plugin"
}
```

The `name` field is the only required field. It must be kebab-case with no spaces.

### Complete Schema

```json
{
  "name": "my-plugin",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://github.com/author"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "commands": ["./custom/commands/special.md"],
  "agents": "./custom/agents/",
  "skills": "./custom/skills/",
  "hooks": "./config/hooks.json",
  "mcpServers": "./mcp-config.json",
  "lspServers": "./.lsp.json",
  "outputStyles": "./styles/"
}
```

### Required Fields

| Field  | Type   | Description                               | Example              |
| ------ | ------ | ----------------------------------------- | -------------------- |
| `name` | string | Unique identifier (kebab-case, no spaces) | `"deployment-tools"` |

### Metadata Fields

| Field         | Type   | Description                         | Example                                            |
| ------------- | ------ | ----------------------------------- | -------------------------------------------------- |
| `version`     | string | Semantic version                    | `"2.1.0"`                                          |
| `description` | string | Brief explanation of plugin purpose | `"Deployment automation tools"`                    |
| `author`      | object | Author information                  | `{"name": "Dev Team", "email": "dev@company.com"}` |
| `homepage`    | string | Documentation URL                   | `"https://docs.example.com"`                       |
| `repository`  | string | Source code URL                     | `"https://github.com/user/plugin"`                 |
| `license`     | string | License identifier                  | `"MIT"`, `"Apache-2.0"`                            |
| `keywords`    | array  | Discovery tags                      | `["deployment", "ci-cd"]`                          |

### Component Path Fields

| Field          | Type           | Default Location   | Description                       |
| -------------- | -------------- | ------------------ | --------------------------------- |
| `commands`     | string\|array  | `commands/`        | Additional command files/dirs     |
| `agents`       | string\|array  | `agents/`          | Additional agent files            |
| `skills`       | string\|array  | `skills/`          | Additional skill directories      |
| `hooks`        | string\|object | `hooks/hooks.json` | Hook config path or inline config |
| `mcpServers`   | string\|object | `.mcp.json`        | MCP config path or inline config  |
| `lspServers`   | string\|object | `.lsp.json`        | LSP config path or inline config  |
| `outputStyles` | string\|array  | -                  | Output style files/dirs           |

Custom paths **supplement** default directories. If `commands/` exists at the root, it is loaded in addition to any custom command paths.

### Path Behavior Rules

All paths must be relative to the plugin root and start with `./`. Multiple paths can be specified as arrays:

```json
{
  "commands": ["./specialized/deploy.md", "./utilities/batch-process.md"],
  "agents": ["./custom-agents/reviewer.md", "./custom-agents/tester.md"]
}
```

Plugins cannot reference files outside their directory. Path traversal (`../`) does not work because plugins are copied to a cache directory during installation.

## Version Management

Follow semantic versioning (`MAJOR.MINOR.PATCH`):

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward-compatible additions)
- **PATCH**: Bug fixes (backward-compatible fixes)

Start at `1.0.0` for the first stable release. Pre-release versions like `2.0.0-beta.1` are supported for testing.

## Complete Plugin Example

A deployment-tools plugin with commands, agents, skills, hooks, and MCP server:

```sh
deployment-tools/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── deploy.md
│   ├── rollback.md
│   └── status.md
├── agents/
│   └── deployment-checker.md
├── skills/
│   └── infrastructure/
│       ├── SKILL.md
│       └── scripts/
│           └── validate-config.py
├── hooks/
│   └── hooks.json
├── .mcp.json
├── scripts/
│   ├── pre-deploy.sh
│   └── notify.py
├── LICENSE
└── CHANGELOG.md
```

### plugin.json

```json
{
  "name": "deployment-tools",
  "version": "2.1.0",
  "description": "Deployment automation for Claude Code",
  "author": {
    "name": "DevOps Team",
    "email": "devops@company.com"
  },
  "repository": "https://github.com/company/deployment-tools",
  "license": "MIT",
  "keywords": ["deployment", "ci-cd", "automation"]
}
```

### hooks.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/pre-deploy.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify.py"
          }
        ]
      }
    ]
  }
}
```

### .mcp.json

```json
{
  "mcpServers": {
    "deployment-api": {
      "command": "npx",
      "args": ["@company/deploy-mcp-server"],
      "cwd": "${CLAUDE_PLUGIN_ROOT}",
      "env": {
        "CONFIG_PATH": "${CLAUDE_PLUGIN_ROOT}/config.json"
      }
    }
  }
}
```

## Plugin Caching

When installed, plugins are copied to a cache directory rather than used in-place. This means:

- Files outside the plugin directory are not available after installation
- Symlinks within the plugin directory are followed during copying
- All file references must use `${CLAUDE_PLUGIN_ROOT}` to resolve correctly regardless of installation location
