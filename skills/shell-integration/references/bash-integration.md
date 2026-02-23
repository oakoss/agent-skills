---
title: Bash Integration
description: Readline configuration, programmable completion (complete/compgen/COMP_WORDS), PROMPT_COMMAND, shopt options, and Bash-specific patterns
tags:
  [
    bash,
    readline,
    complete,
    compgen,
    COMP_WORDS,
    COMP_CWORD,
    COMPREPLY,
    PROMPT_COMMAND,
    shopt,
  ]
---

# Bash Integration

## Readline Configuration

Readline controls line editing behavior in Bash. Configure via `~/.inputrc` or `bind` builtin.

```text
# ~/.inputrc
$if Bash
  set show-all-if-ambiguous on
  set completion-ignore-case on
  set colored-stats on
  set mark-symlinked-directories on
  set show-all-if-unmodified on
  set visible-stats on
$endif

# Vi mode
set editing-mode vi

# Custom bindings
"\C-r": reverse-search-history
"\C-p": history-search-backward
"\C-n": history-search-forward
"\e[A": history-search-backward
"\e[B": history-search-forward
```

### Bind Builtin

```bash
bind '"\C-x\C-r": re-read-init-file'
bind 'set show-all-if-ambiguous on'
bind -x '"\C-l": clear'

# List current bindings
bind -P | grep -v "not bound"
```

## Programmable Completion

### Core Variables

| Variable     | Purpose                                  |
| ------------ | ---------------------------------------- |
| `COMP_WORDS` | Array of words on the command line       |
| `COMP_CWORD` | Index into `COMP_WORDS` for current word |
| `COMP_LINE`  | Full command line string                 |
| `COMP_POINT` | Cursor position in `COMP_LINE`           |
| `COMPREPLY`  | Array of completions to return           |

### Basic Completion Function

```bash
_mytool() {
  local cur prev opts
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"
  opts="--help --verbose --config init build deploy"

  case "$prev" in
    --config)
      COMPREPLY=($(compgen -f -X '!*.toml' -- "$cur"))
      return 0
      ;;
  esac

  COMPREPLY=($(compgen -W "$opts" -- "$cur"))
}

complete -F _mytool mytool
```

### Compgen Actions

```bash
# Complete with files
compgen -f -- "$cur"

# Complete with directories only
compgen -d -- "$cur"

# Complete with commands
compgen -c -- "$cur"

# Complete with variables
compgen -v -- "$cur"

# Complete with word list
compgen -W "start stop restart" -- "$cur"

# Complete with function output
compgen -W "$(mytool --list-commands 2>/dev/null)" -- "$cur"

# File extension filter
compgen -f -X '!*.json' -- "$cur"
```

### Subcommand Completion

```bash
_mytool() {
  local cur prev words cword
  _init_completion || return

  if [[ $cword -eq 1 ]]; then
    COMPREPLY=($(compgen -W "deploy config status" -- "$cur"))
    return
  fi

  case "${words[1]}" in
    deploy)
      case "$prev" in
        --env)
          COMPREPLY=($(compgen -W "staging production" -- "$cur"))
          ;;
        *)
          COMPREPLY=($(compgen -W "--env --dry-run --force" -- "$cur"))
          ;;
      esac
      ;;
    config)
      COMPREPLY=($(compgen -W "set get list" -- "$cur"))
      ;;
  esac
}

complete -F _mytool mytool
```

### Using bash-completion Helpers

```bash
# _init_completion sets cur, prev, words, cword
_mytool() {
  local cur prev words cword
  _init_completion -n : || return

  # _filedir completes files with optional extension filter
  case "$prev" in
    --config)
      _filedir toml
      ;;
    --output)
      _filedir
      ;;
    *)
      COMPREPLY=($(compgen -W "--config --output --help" -- "$cur"))
      ;;
  esac
}

complete -F _mytool mytool
```

## PROMPT_COMMAND

### Single Command (All Bash Versions)

```bash
_update_title() {
  printf '\e]0;%s\a' "${PWD/#$HOME/~}"
}

PROMPT_COMMAND="_update_title"
```

### Array Form (Bash 5.1+)

```bash
# Append without overwriting other tools
PROMPT_COMMAND+=("_my_precmd")

_my_precmd() {
  local exit_code=$?
  history -a
  _update_title
  return $exit_code
}
```

### Safe Append (All Versions)

```bash
# Works with both string and array PROMPT_COMMAND
_append_prompt_command() {
  if [[ "${BASH_VERSINFO[0]}" -ge 5 && "${BASH_VERSINFO[1]}" -ge 1 ]]; then
    PROMPT_COMMAND+=("$1")
  else
    PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND;} $1"
  fi
}

_append_prompt_command "_my_precmd"
```

## Shopt Options

### Useful Options for Plugins

```bash
# Glob patterns that match no files expand to null string
shopt -s nullglob

# ** matches directories recursively
shopt -s globstar

# Case-insensitive globbing
shopt -s nocaseglob

# Extended pattern matching: ?(pat), *(pat), +(pat), @(pat), !(pat)
shopt -s extglob

# Append to history instead of overwriting
shopt -s histappend

# Check window size after each command
shopt -s checkwinsize

# cd into directory by typing its name
shopt -s autocd

# Correct minor cd spelling errors
shopt -s cdspell
```

### Checking Options

```bash
if shopt -q globstar; then
  echo "globstar is enabled"
fi

# Save and restore option state
local saved_nullglob
saved_nullglob=$(shopt -p nullglob)
shopt -s nullglob
# ... do work ...
eval "$saved_nullglob"
```

## Preexec Equivalent in Bash

Bash lacks a native preexec hook. The common pattern uses `DEBUG` trap:

```bash
_preexec_hook() {
  # $BASH_COMMAND contains the command about to execute
  if [[ "$BASH_COMMAND" != "$PROMPT_COMMAND" ]]; then
    printf '\e]0;%s\a' "$BASH_COMMAND"
  fi
}

trap '_preexec_hook' DEBUG
```

## Bash Version Detection

```bash
if [[ "${BASH_VERSINFO[0]}" -lt 4 ]]; then
  echo "Bash 4+ required for associative arrays" >&2
  return 1
fi

if [[ "${BASH_VERSINFO[0]}" -eq 4 && "${BASH_VERSINFO[1]}" -lt 3 ]]; then
  echo "Bash 4.3+ required for nameref" >&2
  return 1
fi
```

## Associative Arrays (Bash 4+)

```bash
declare -A config=(
  [host]="localhost"
  [port]="8080"
)

for key in "${!config[@]}"; do
  printf '%s=%s\n' "$key" "${config[$key]}"
done
```
