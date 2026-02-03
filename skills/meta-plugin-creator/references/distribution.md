---
title: Distribution
description: Installation scopes, environment variables, marketplace publishing, and CLI commands
tags:
  [installation, scopes, environment-variables, marketplace, publishing, cli]
---

# Distribution

## Installation Scopes

When installing a plugin, choose a scope that determines availability and visibility:

| Scope     | Settings File                 | Use Case                                 |
| --------- | ----------------------------- | ---------------------------------------- |
| `user`    | `~/.claude/settings.json`     | Personal plugins, all projects (default) |
| `project` | `.claude/settings.json`       | Team plugins, version controlled         |
| `local`   | `.claude/settings.local.json` | Project-specific, gitignored             |
| `managed` | `managed-settings.json`       | Enterprise, read-only (update only)      |

Install with a specific scope:

```bash
claude plugin install formatter@my-marketplace --scope project
```

## Environment Variables

### Plugin Path Variables

| Variable                | Purpose                                   |
| ----------------------- | ----------------------------------------- |
| `${CLAUDE_PLUGIN_ROOT}` | Absolute path to plugin install directory |
| `${CLAUDE_PROJECT_DIR}` | Project root directory                    |

Always use `${CLAUDE_PLUGIN_ROOT}` for paths to files within the plugin. Absolute paths break when the plugin is installed to a different location.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/process.sh"
          }
        ]
      }
    ]
  }
}
```

### Auto-Update Configuration

Control auto-update behavior for plugins and Claude Code:

| Variable                   | Effect                                                |
| -------------------------- | ----------------------------------------------------- |
| `DISABLE_AUTOUPDATER`      | Disables all auto-updates (plugins and Claude Code)   |
| `FORCE_AUTOUPDATE_PLUGINS` | Enables plugin updates even when autoupdater disabled |

```bash
# Disable all auto-updates
export DISABLE_AUTOUPDATER=true

# Keep plugin updates, disable Claude Code updates
export DISABLE_AUTOUPDATER=true
export FORCE_AUTOUPDATE_PLUGINS=true
```

## CLI Commands

### Plugin Management

```bash
claude plugin install <plugin> [--scope user|project|local]
claude plugin uninstall <plugin> [--scope user|project|local]
claude plugin enable <plugin> [--scope user|project|local]
claude plugin disable <plugin> [--scope user|project|local]
claude plugin update <plugin> [--scope user|project|local|managed]
claude plugin validate .
```

### Local Development

Test a plugin without installation:

```bash
claude --plugin-dir ./my-plugin
```

Load multiple plugins simultaneously:

```bash
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
```

### Interactive UI

```bash
/plugin              # Open plugin manager
```

Tabs:

- **Discover**: Browse available plugins from connected marketplaces
- **Installed**: Manage installed plugins (enable, disable, uninstall)
- **Marketplaces**: Add/remove marketplaces
- **Errors**: View loading errors for troubleshooting

### Debugging

```bash
claude --debug
```

Shows plugin loading details, manifest errors, component registration, and MCP server initialization.

#### Common Issues

| Issue                | Cause                           | Solution                                     |
| -------------------- | ------------------------------- | -------------------------------------------- |
| Plugin not loading   | Invalid `plugin.json`           | Validate JSON syntax                         |
| Commands missing     | Wrong directory                 | Components at root, not in `.claude-plugin/` |
| Hooks not firing     | Script not executable           | `chmod +x script.sh`                         |
| MCP server fails     | Missing `${CLAUDE_PLUGIN_ROOT}` | Use variable for paths                       |
| LSP not found        | Binary not installed            | Install language server                      |
| Skills not appearing | Cache stale                     | Clear cache, reinstall                       |

#### Debug Checklist

1. Run `claude --debug` and check "loading plugin" messages
2. Verify component directories appear in debug output
3. Check file permissions on scripts
4. Test scripts manually outside Claude
5. Validate JSON syntax in all config files
6. Clear cache if needed: `rm -rf ~/.claude/plugins/cache`

## Marketplace Publishing

### Marketplace Structure

A marketplace is a git repository with `.claude-plugin/marketplace.json`:

```json
{
  "name": "company-tools",
  "owner": {
    "name": "DevTools Team",
    "email": "devtools@example.com"
  },
  "metadata": {
    "description": "Internal development tools",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "code-formatter",
      "source": "./plugins/formatter",
      "description": "Automatic code formatting",
      "version": "2.1.0"
    }
  ]
}
```

### Required Marketplace Fields

| Field     | Type   | Description                         |
| --------- | ------ | ----------------------------------- |
| `name`    | string | Marketplace identifier (kebab-case) |
| `owner`   | object | Maintainer info (`name` required)   |
| `plugins` | array  | List of plugin entries              |

### Plugin Entry Fields

Each entry requires `name` and `source`. The `source` can be:

**Relative path** (same repository):

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin"
}
```

**GitHub repository**:

```json
{
  "name": "github-plugin",
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo",
    "ref": "v2.0.0"
  }
}
```

**Git URL**:

```json
{
  "name": "git-plugin",
  "source": {
    "source": "url",
    "url": "https://gitlab.com/team/plugin.git"
  }
}
```

### The `strict` Field

| Value            | Behavior                                                      |
| ---------------- | ------------------------------------------------------------- |
| `true` (default) | Plugin source must contain its own `plugin.json`              |
| `false`          | Marketplace entry defines everything; no `plugin.json` needed |

When `strict: true`, fields in the marketplace entry merge with the plugin's own `plugin.json`.

### Marketplace CLI

```bash
# Add a marketplace
/plugin marketplace add owner/repo
/plugin marketplace add https://gitlab.com/team/plugins.git
/plugin marketplace add ./local-marketplace

# Update marketplace catalog
/plugin marketplace update

# Install from marketplace
/plugin install my-plugin@marketplace-name
```

## Team Distribution

### Auto-Prompt Installation

Add marketplace to `.claude/settings.json` so team members are prompted to install:

```json
{
  "extraKnownMarketplaces": {
    "company-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "formatter@company-tools": true,
    "deploy-tools@company-tools": true
  }
}
```

### Private Repository Access

For background auto-updates of private marketplace repos, set authentication tokens:

| Provider  | Environment Variables        |
| --------- | ---------------------------- |
| GitHub    | `GITHUB_TOKEN` or `GH_TOKEN` |
| GitLab    | `GITLAB_TOKEN` or `GL_TOKEN` |
| Bitbucket | `BITBUCKET_TOKEN`            |

Manual installation and updates use existing git credential helpers.

## Official Marketplace Plugins

### Code Intelligence (LSP)

- `pyright-lsp` — Python type checking
- `typescript-lsp` — TypeScript/JavaScript
- `rust-analyzer-lsp` — Rust
- `gopls-lsp` — Go
- `clangd-lsp` — C/C++

### External Integrations (MCP)

- `github`, `gitlab` — Source control
- `atlassian`, `linear`, `notion` — Project management
- `slack` — Communication
- `vercel`, `firebase`, `supabase` — Infrastructure

### Development Workflows

- `commit-commands` — Git workflows
- `pr-review-toolkit` — PR review agents
- `plugin-dev` — Plugin development toolkit

## Validation Checklist

Before publishing, verify:

- `.claude-plugin/plugin.json` exists with at least a `name` field
- All component directories are at plugin root, not inside `.claude-plugin/`
- All paths are relative, starting with `./`
- Scripts are executable (`chmod +x`)
- All file references use `${CLAUDE_PLUGIN_ROOT}`
- Version follows semver (`MAJOR.MINOR.PATCH`)
- `claude plugin validate .` passes with no errors
