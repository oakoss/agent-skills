---
title: Zsh Integration
description: ZLE widgets, completion system (compdef/compadd/zstyle), hooks (precmd/preexec/chpwd), bindkey, parameter expansion, and ZDOTDIR loading order
tags:
  [
    zsh,
    zle,
    compdef,
    compadd,
    zstyle,
    precmd,
    preexec,
    chpwd,
    bindkey,
    parameter-expansion,
    zdotdir,
  ]
---

# Zsh Integration

## ZDOTDIR Loading Order

Zsh reads startup files in a specific order. Understanding this is critical for plugin installation.

```text
/etc/zshenv        -> $ZDOTDIR/.zshenv       (always, every shell)
/etc/zprofile      -> $ZDOTDIR/.zprofile      (login shells only)
/etc/zshrc         -> $ZDOTDIR/.zshrc         (interactive shells only)
/etc/zlogin        -> $ZDOTDIR/.zlogin        (login shells only, after .zshrc)
/etc/zlogout       -> $ZDOTDIR/.zlogout       (login shells only, on exit)
```

`ZDOTDIR` defaults to `$HOME` if unset. Plugins targeting interactive use belong in `.zshrc`.

## ZLE Widgets

ZLE (Zsh Line Editor) widgets are functions bound to key sequences for custom line editing behavior.

```zsh
my-widget() {
  emulate -L zsh
  BUFFER="modified: $BUFFER"
  CURSOR=$#BUFFER
}

zle -N my-widget
bindkey '^X^M' my-widget
```

Key ZLE variables available inside widgets:

```zsh
$BUFFER    # Full command line contents
$LBUFFER   # Text left of cursor
$RBUFFER   # Text right of cursor
$CURSOR    # Cursor position (0-indexed)
$WIDGET    # Name of the widget being executed
$KEYMAP    # Current keymap name
$KEYS      # Keys that invoked the widget
```

### Accept-Line Wrapper

Intercept Enter to add validation or transformation before execution:

```zsh
custom-accept-line() {
  emulate -L zsh
  if [[ "$BUFFER" == *"rm -rf /"* ]]; then
    zle -M "Blocked dangerous command"
    return 1
  fi
  zle .accept-line
}
zle -N accept-line custom-accept-line
```

### Widget with Completion

```zsh
fzf-history-widget() {
  emulate -L zsh
  setopt localoptions pipefail
  local selected
  selected=$(fc -rln 1 | fzf --height 40% --reverse)
  if [[ -n "$selected" ]]; then
    BUFFER="$selected"
    CURSOR=$#BUFFER
  fi
  zle reset-prompt
}
zle -N fzf-history-widget
bindkey '^R' fzf-history-widget
```

## Completion System

### Basic Completion Function

```zsh
#compdef mytool

_mytool() {
  local -a commands
  commands=(
    'init:Initialize a new project'
    'build:Build the project'
    'deploy:Deploy to production'
  )

  _arguments \
    '(-h --help)'{-h,--help}'[Show help]' \
    '(-v --verbose)'{-v,--verbose}'[Enable verbose output]' \
    '--config[Config file]:file:_files -g "*.toml"' \
    '1:command:->cmd'

  case "$state" in
    cmd)
      _describe 'command' commands
      ;;
  esac
}

_mytool
```

### Subcommand Completion

```zsh
#compdef mytool

_mytool() {
  local curcontext="$curcontext" state line
  typeset -A opt_args

  _arguments -C \
    '1:command:->cmd' \
    '*::arg:->args'

  case "$state" in
    cmd)
      local -a commands=(
        'deploy:Deploy the application'
        'config:Manage configuration'
      )
      _describe 'command' commands
      ;;
    args)
      case "${line[1]}" in
        deploy)
          _arguments \
            '--env[Target environment]:env:(staging production)' \
            '--dry-run[Preview changes]'
          ;;
        config)
          _arguments \
            'set:Set a value' \
            'get:Get a value'
          ;;
      esac
      ;;
  esac
}

_mytool
```

### Compadd Direct Usage

For low-level control over completion candidates:

```zsh
_mytool_branches() {
  local -a branches
  branches=(${(f)"$(git branch --format='%(refname:short)' 2>/dev/null)"})
  compadd -V branches -d branches -- "${branches[@]}"
}
```

### Zstyle Configuration

```zsh
# Case-insensitive matching
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# Group completions by category
zstyle ':completion:*' group-name ''
zstyle ':completion:*:descriptions' format '%B%d%b'

# Cache completions for expensive operations
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "$HOME/.zcompcache"

# Menu selection with highlighting
zstyle ':completion:*' menu select
zstyle ':completion:*:default' list-colors ${(s.:.)LS_COLORS}
```

## Hooks

### Using add-zsh-hook

```zsh
autoload -Uz add-zsh-hook

my_precmd() {
  # Runs before each prompt display
  print -Pn "\e]0;%~\a"
}
add-zsh-hook precmd my_precmd

my_preexec() {
  # Runs after command is read, before execution
  # $1 = the command string as typed
  # $2 = single-line expanded version
  # $3 = full expanded command
  timer_start=$EPOCHSECONDS
}
add-zsh-hook preexec my_preexec

my_chpwd() {
  # Runs when working directory changes
  ls
}
add-zsh-hook chpwd my_chpwd
```

### Available Hook Points

| Hook            | Trigger                         | Common Use                |
| --------------- | ------------------------------- | ------------------------- |
| `precmd`        | Before prompt display           | Update prompt, set title  |
| `preexec`       | After command read, before exec | Start timer, log command  |
| `chpwd`         | Directory change                | Auto-ls, update env       |
| `periodic`      | Every `$PERIOD` seconds         | Background checks         |
| `zshaddhistory` | Before history write            | Filter sensitive commands |
| `zshexit`       | Shell exit                      | Cleanup                   |

## Bindkey and Keymaps

```zsh
# List current bindings
bindkey -L

# Bind in specific keymap
bindkey -M viins '^A' beginning-of-line
bindkey -M vicmd 'k' up-line-or-history

# Create custom keymap
bindkey -N mymap
bindkey -M mymap '^X' my-widget

# Common key sequences
bindkey '^[[A' up-line-or-search      # Up arrow
bindkey '^[[B' down-line-or-search    # Down arrow
bindkey '^[[3~' delete-char           # Delete key
```

## Parameter Expansion

### Flags

```zsh
str="hello:world:foo"

# Split on delimiter
print -l ${(s.:.)str}        # hello\nworld\nfoo

# Join array
arr=(hello world foo)
print ${(j.:.)arr}           # hello:world:foo

# Uppercase / lowercase
print ${(U)str}              # HELLO:WORLD:FOO
print ${(L)str}              # hello:world:foo

# Length
print ${#str}                # 15

# Unique elements
arr=(a b a c b)
print ${(u)arr}              # a b c
```

### Modifiers

```zsh
path="/home/user/file.tar.gz"

print ${path:h}     # /home/user        (head/dirname)
print ${path:t}     # file.tar.gz       (tail/basename)
print ${path:r}     # /home/user/file.tar (remove extension)
print ${path:e}     # gz                 (extension)
print ${path:A}     # /home/user/file.tar.gz (absolute path)
```

### Defaults and Substitution

```zsh
# Default if unset
print ${var:-default}

# Assign default if unset
: ${var:=default}

# Error if unset
: ${var:?'var must be set'}

# Substitute if set
print ${var:+is_set}

# Pattern substitution
str="hello world"
print ${str/world/zsh}       # hello zsh
print ${str//o/0}            # hell0 w0rld
```

## Emulate for Safety

Always use `emulate -L zsh` at the top of plugin functions to ensure consistent behavior regardless of the user's option settings:

```zsh
my_plugin_func() {
  emulate -L zsh
  setopt extended_glob no_unset pipe_fail
  # Function body with known option state
}
```
