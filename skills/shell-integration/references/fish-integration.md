---
title: Fish Integration
description: Fish completion system (complete command), event system, abbreviations, functions, and configuration patterns
tags:
  [
    fish,
    complete,
    event,
    abbreviation,
    abbr,
    function,
    config,
    universal-variables,
  ]
---

# Fish Integration

## Configuration

Fish reads `~/.config/fish/config.fish` on startup for interactive shells. Functions in `~/.config/fish/functions/` are autoloaded on first call.

```text
~/.config/fish/
├── config.fish              # Startup config (interactive)
├── conf.d/                  # Drop-in config fragments (sourced alphabetically)
│   └── plugin.fish
├── functions/               # Autoloaded functions (one per file)
│   └── mytool.fish
└── completions/             # Autoloaded completions (one per command)
    └── mytool.fish
```

## Completion System

### Basic Completion

```fish
# completions/mytool.fish
complete -c mytool -s h -l help -d "Show help"
complete -c mytool -s v -l verbose -d "Enable verbose output"
complete -c mytool -l config -r -F -d "Config file"

# Subcommands
complete -c mytool -n "__fish_use_subcommand" -a init -d "Initialize project"
complete -c mytool -n "__fish_use_subcommand" -a build -d "Build project"
complete -c mytool -n "__fish_use_subcommand" -a deploy -d "Deploy to production"
```

### Subcommand Options

```fish
# Options specific to "deploy" subcommand
complete -c mytool -n "__fish_seen_subcommand_from deploy" -l env -r -a "staging production" -d "Target environment"
complete -c mytool -n "__fish_seen_subcommand_from deploy" -l dry-run -d "Preview changes"

# Options specific to "config" subcommand
complete -c mytool -n "__fish_seen_subcommand_from config" -a "set get list" -d "Config action"
```

### Completion Flags Reference

| Flag           | Purpose                                                       |
| -------------- | ------------------------------------------------------------- |
| `-c CMD`       | Command to complete for                                       |
| `-s CHAR`      | Short option                                                  |
| `-l STRING`    | Long option                                                   |
| `-a ARGS`      | List of completions (space-separated or command substitution) |
| `-r`           | Option requires an argument                                   |
| `-f`           | Do not complete with files                                    |
| `-F`           | Complete with files (default, use to override `-f`)           |
| `-n CONDITION` | Only offer completion when condition is true                  |
| `-d DESC`      | Description for the completion                                |
| `-x`           | Shorthand for `-r -f` (exclusive, requires arg, no files)     |
| `-k`           | Keep order of completions (do not sort)                       |

### Dynamic Completions

```fish
complete -c mytool -n "__fish_seen_subcommand_from checkout" -a "(mytool list-branches 2>/dev/null)" -d "Branch"

# Custom condition function
function __mytool_needs_subcommand
    set -l cmd (commandline -opc)
    test (count $cmd) -eq 1
end

complete -c mytool -n "__mytool_needs_subcommand" -a "init build deploy"
```

### Built-in Condition Functions

```fish
__fish_use_subcommand              # No subcommand typed yet
__fish_seen_subcommand_from CMD    # Specific subcommand was typed
__fish_complete_directories        # Complete directories
__fish_complete_users              # Complete usernames
__fish_complete_groups             # Complete group names
__fish_complete_pids               # Complete process IDs
```

## Event System

### Named Events

```fish
function on_myevent --on-event myevent
    echo "myevent fired with args: $argv"
end

emit myevent arg1 arg2
```

### Variable Watch Events

```fish
function on_pwd_change --on-variable PWD
    echo "Changed to $PWD"
end

function on_path_change --on-variable fish_user_paths
    echo "PATH updated"
end
```

### Signal Events

```fish
function on_winch --on-signal WINCH
    echo "Terminal resized"
end

function cleanup --on-signal INT
    echo "Caught SIGINT"
    exit 1
end
```

### Process Events

```fish
function notify_done --on-process-exit %self
    echo "Shell exiting"
end

function job_done --on-job-exit (jobs -lp | tail -1)
    echo "Background job completed"
end
```

### Built-in Events

| Event           | Trigger                  |
| --------------- | ------------------------ |
| `fish_prompt`   | Before prompt display    |
| `fish_preexec`  | Before command execution |
| `fish_postexec` | After command execution  |
| `fish_exit`     | Shell exit               |
| `fish_cancel`   | Command line cancelled   |

```fish
function log_command --on-event fish_preexec
    echo (date +%T) $argv[1] >> ~/.fish_command_log
end
```

## Abbreviations

### Basic Abbreviations

```fish
abbr -a gco "git checkout"
abbr -a gst "git status"
abbr -a ll "ls -la"
```

### Position-Aware Abbreviations

```fish
# Only expand at command position (not as argument)
abbr -a --position command g git

# Only expand as argument (not as command)
abbr -a --position anywhere !! "$history[1]"
```

### Dynamic Abbreviations (Function)

```fish
function _last_history_item
    echo $history[1]
end

abbr -a !! --position anywhere --function _last_history_item
```

### Regex Abbreviations

```fish
abbr -a dotdot --regex '^\.\.+$' --function _expand_dots

function _expand_dots
    string repeat -n (math (string length -- $argv[1]) - 1) "../"
end
```

## Functions

### Autoloaded Function

```fish
# ~/.config/fish/functions/mytool.fish
function mytool -d "My custom tool"
    switch $argv[1]
        case init
            echo "Initializing..."
        case build
            echo "Building..."
        case '*'
            echo "Usage: mytool {init|build}" >&2
            return 1
    end
end
```

### Function with Options

```fish
function serve -d "Start dev server"
    argparse h/help 'p/port=!_validate_int' -- $argv
    or return

    if set -q _flag_help
        echo "Usage: serve [-p PORT]"
        return 0
    end

    set -l port ($_flag_port; or echo 3000)
    echo "Serving on port $port"
end
```

## Universal Variables

Fish universal variables persist across sessions and sync between running instances:

```fish
# Set (persists and syncs across all fish sessions)
set -U EDITOR nvim
set -U fish_user_paths $HOME/.local/bin $fish_user_paths

# Remove
set -e -U fish_user_paths[1]
```

## Version Detection

```fish
if test (string match -r '\d+' $FISH_VERSION) -ge 4
    echo "Fish 4.x features available"
end

set -l fish_major (string split . $FISH_VERSION)[1]
if test "$fish_major" -lt 3
    echo "Fish 3+ required" >&2
    return 1
end
```
