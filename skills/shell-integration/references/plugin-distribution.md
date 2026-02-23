---
title: Plugin Distribution
description: Shell plugin installation scripts, dotfile management, sourcing strategies, version detection, and graceful degradation
tags:
  [
    plugin,
    installation,
    dotfile,
    sourcing,
    version-detection,
    degradation,
    distribution,
    package-manager,
  ]
---

# Plugin Distribution

## Installation Script Pattern

```sh
#!/bin/sh
set -eu

INSTALL_DIR="${HOME}/.local/share/mytool"
BIN_DIR="${HOME}/.local/bin"

main() {
  detect_platform
  download_binary
  install_shell_integration
  print_instructions
}

detect_platform() {
  OS=$(uname -s | tr '[:upper:]' '[:lower:]')
  ARCH=$(uname -m)
  case "$ARCH" in
    x86_64|amd64) ARCH="x86_64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    *) die "Unsupported architecture: $ARCH" ;;
  esac
}

download_binary() {
  local url="https://github.com/org/mytool/releases/latest/download/mytool-${OS}-${ARCH}"
  mkdir -p "$BIN_DIR"

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "${BIN_DIR}/mytool"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "${BIN_DIR}/mytool" "$url"
  else
    die "curl or wget required"
  fi
  chmod +x "${BIN_DIR}/mytool"
}

install_shell_integration() {
  mkdir -p "$INSTALL_DIR"
  "${BIN_DIR}/mytool" --generate-completions zsh > "$INSTALL_DIR/completions.zsh" 2>/dev/null || true
  "${BIN_DIR}/mytool" --generate-completions bash > "$INSTALL_DIR/completions.bash" 2>/dev/null || true
  "${BIN_DIR}/mytool" --generate-completions fish > "$INSTALL_DIR/completions.fish" 2>/dev/null || true
}

print_instructions() {
  cat <<'EOF'
Installation complete!

Add to your shell config:

  # Bash (~/.bashrc)
  eval "$(mytool init bash)"

  # Zsh (~/.zshrc)
  eval "$(mytool init zsh)"

  # Fish (~/.config/fish/config.fish)
  mytool init fish | source
EOF
}

die() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

main "$@"
```

## Shell Init Command Pattern

Many tools generate shell integration via a `tool init <shell>` command:

```sh
# The init command outputs shell code to stdout
mytool_init_zsh() {
  cat <<'INIT'
_mytool_hook() {
  emulate -L zsh
  eval "$(mytool hook zsh)"
}
add-zsh-hook precmd _mytool_hook

if [[ -f "${MYTOOL_DIR}/completions.zsh" ]]; then
  source "${MYTOOL_DIR}/completions.zsh"
fi
INIT
}

mytool_init_bash() {
  cat <<'INIT'
_mytool_hook() {
  eval "$(mytool hook bash)"
}
PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND;} _mytool_hook"

if [[ -f "${MYTOOL_DIR}/completions.bash" ]]; then
  source "${MYTOOL_DIR}/completions.bash"
fi
INIT
}

mytool_init_fish() {
  cat <<'INIT'
function _mytool_hook --on-event fish_prompt
  mytool hook fish | source
end

if test -f "$MYTOOL_DIR/completions.fish"
  source "$MYTOOL_DIR/completions.fish"
end
INIT
}
```

## Sourcing Strategies

### Direct Sourcing

```sh
# Zsh: simple but runs every shell startup
source "$HOME/.local/share/mytool/init.zsh"
```

### Lazy Loading (Zsh)

Defer loading until the command is first used:

```zsh
mytool() {
  unfunction mytool
  eval "$(command mytool init zsh)"
  mytool "$@"
}
```

### Cached Eval

Cache the init output to avoid running the binary on every shell startup:

```sh
_mytool_cache="$HOME/.cache/mytool/init.zsh"

if [ ! -f "$_mytool_cache" ] || [ "$(mytool --version 2>/dev/null)" != "$(head -1 "$_mytool_cache" 2>/dev/null)" ]; then
  mkdir -p "${_mytool_cache%/*}"
  {
    mytool --version
    mytool init zsh
  } > "$_mytool_cache" 2>/dev/null
fi

source "$_mytool_cache"
```

### Compile Zsh Scripts

```zsh
# Compile for faster loading
if [[ ! -f "${init_script}.zwc" ]] || [[ "$init_script" -nt "${init_script}.zwc" ]]; then
  zcompile "$init_script"
fi
source "$init_script"
```

## Shell Detection

```sh
detect_shell() {
  local shell_name
  shell_name=$(basename "$SHELL")
  case "$shell_name" in
    zsh)  echo "zsh" ;;
    bash) echo "bash" ;;
    fish) echo "fish" ;;
    *)    echo "unknown" ;;
  esac
}

# More reliable: check current running shell
detect_current_shell() {
  if [ -n "${ZSH_VERSION:-}" ]; then
    echo "zsh"
  elif [ -n "${BASH_VERSION:-}" ]; then
    echo "bash"
  elif [ -n "${FISH_VERSION:-}" ]; then
    echo "fish"
  else
    echo "sh"
  fi
}
```

## Version Detection and Feature Gating

```sh
# Zsh version check
check_zsh_version() {
  if [ -n "${ZSH_VERSION:-}" ]; then
    autoload -Uz is-at-least
    if ! is-at-least 5.2; then
      echo "Warning: Zsh 5.2+ recommended" >&2
      return 1
    fi
  fi
}

# Bash version check
check_bash_version() {
  if [ -n "${BASH_VERSION:-}" ]; then
    local major="${BASH_VERSINFO[0]}"
    local minor="${BASH_VERSINFO[1]}"
    if [ "$major" -lt 4 ] || { [ "$major" -eq 4 ] && [ "$minor" -lt 0 ]; }; then
      echo "Warning: Bash 4+ recommended" >&2
      return 1
    fi
  fi
}

# Feature gating
setup_completions() {
  if [ -n "${ZSH_VERSION:-}" ]; then
    setup_zsh_completions
  elif [ -n "${BASH_VERSION:-}" ]; then
    if [ "${BASH_VERSINFO[0]}" -ge 4 ]; then
      setup_bash4_completions
    else
      setup_bash3_completions
    fi
  fi
}
```

## Dotfile Management

### XDG Base Directory Compliance

```sh
config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/mytool"
data_dir="${XDG_DATA_HOME:-$HOME/.local/share}/mytool"
cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/mytool"
state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/mytool"

mkdir -p "$config_dir" "$data_dir" "$cache_dir" "$state_dir"
```

### Safe Config File Modification

```sh
add_to_shell_config() {
  local config_file="$1"
  local init_line="$2"
  local marker="# mytool"

  if [ ! -f "$config_file" ]; then
    return 1
  fi

  if grep -qF "$marker" "$config_file" 2>/dev/null; then
    return 0
  fi

  printf '\n%s\n%s\n' "$marker" "$init_line" >> "$config_file"
}

install_to_shell() {
  local shell
  shell=$(detect_shell)

  case "$shell" in
    zsh)
      add_to_shell_config "${ZDOTDIR:-$HOME}/.zshrc" 'eval "$(mytool init zsh)"'
      ;;
    bash)
      add_to_shell_config "$HOME/.bashrc" 'eval "$(mytool init bash)"'
      ;;
    fish)
      local fish_conf="${XDG_CONFIG_HOME:-$HOME/.config}/fish/conf.d"
      mkdir -p "$fish_conf"
      mytool init fish > "$fish_conf/mytool.fish"
      ;;
  esac
}
```

## Uninstallation

```sh
uninstall() {
  rm -f "${BIN_DIR}/mytool"
  rm -rf "${INSTALL_DIR}"

  # Remove from shell configs
  for rc in "$HOME/.bashrc" "$HOME/.zshrc" "${ZDOTDIR:-$HOME}/.zshrc"; do
    if [ -f "$rc" ]; then
      sed -i.bak '/# mytool/d;/mytool init/d' "$rc"
      rm -f "${rc}.bak"
    fi
  done

  # Remove fish config
  rm -f "${XDG_CONFIG_HOME:-$HOME/.config}/fish/conf.d/mytool.fish"
  rm -f "${XDG_CONFIG_HOME:-$HOME/.config}/fish/completions/mytool.fish"
}
```

## Plugin Manager Integration

### Oh My Zsh

```text
# Place in ~/.oh-my-zsh/custom/plugins/mytool/
mytool/
├── mytool.plugin.zsh    # Main entry point (auto-sourced)
└── _mytool              # Completion file (added to fpath)
```

```zsh
# mytool.plugin.zsh
if (( ! $+commands[mytool] )); then
  return
fi
eval "$(mytool init zsh)"
```

### Fisher (Fish)

```text
# Repository structure for Fisher
mytool/
├── conf.d/
│   └── mytool.fish          # Auto-sourced config
├── completions/
│   └── mytool.fish          # Auto-loaded completions
└── functions/
    └── mytool_helper.fish   # Auto-loaded functions
```

### Zinit / Sheldon / Antidote (Zsh)

```zsh
# Zinit
zinit light org/mytool-zsh

# Sheldon (sheldon.toml)
# [plugins.mytool]
# github = "org/mytool-zsh"

# Antidote
# org/mytool-zsh
```

## Graceful Degradation

```sh
init_plugin() {
  if ! command -v mytool >/dev/null 2>&1; then
    _mytool_not_found() {
      echo "mytool not found. Install: https://mytool.dev/install" >&2
      return 127
    }
    alias mytool='_mytool_not_found'
    return
  fi

  local version
  version=$(mytool --version 2>/dev/null | head -1)

  case "$version" in
    1.*)
      eval "$(mytool init-v1 "$current_shell")"
      ;;
    2.*|3.*)
      eval "$(mytool init "$current_shell")"
      ;;
    *)
      echo "Warning: Unknown mytool version ($version), attempting init" >&2
      eval "$(mytool init "$current_shell" 2>/dev/null)" || true
      ;;
  esac
}
```
