---
title: Terminal Control
description: ANSI/CSI escape sequences, tput, stty, TERM capabilities, cursor control, colors, and terminal queries
tags:
  [ansi, csi, escape-sequences, tput, stty, terminal, colors, cursor, terminfo]
---

# Terminal Control

## ANSI/CSI Escape Sequences

CSI (Control Sequence Introducer) sequences start with `ESC [` (`\e[` or `\033[`).

### Cursor Movement

```sh
printf '\e[H'         # Move to home position (1,1)
printf '\e[%d;%dH' 5 10  # Move to row 5, column 10
printf '\e[A'         # Up one line
printf '\e[B'         # Down one line
printf '\e[C'         # Forward one column
printf '\e[D'         # Back one column
printf '\e[%dA' 3     # Up 3 lines
printf '\e[s'         # Save cursor position
printf '\e[u'         # Restore cursor position
printf '\e[6n'        # Query cursor position (response: ESC[row;colR)
```

### Screen Control

```sh
printf '\e[2J'        # Clear entire screen
printf '\e[0J'        # Clear from cursor to end of screen
printf '\e[1J'        # Clear from start of screen to cursor
printf '\e[2K'        # Clear entire line
printf '\e[0K'        # Clear from cursor to end of line
printf '\e[1K'        # Clear from start of line to cursor
```

### Text Attributes

```sh
printf '\e[0m'        # Reset all attributes
printf '\e[1m'        # Bold
printf '\e[2m'        # Dim
printf '\e[3m'        # Italic
printf '\e[4m'        # Underline
printf '\e[7m'        # Reverse (swap fg/bg)
printf '\e[8m'        # Hidden
printf '\e[9m'        # Strikethrough
```

### Colors (SGR)

```sh
# Standard colors (foreground: 30-37, background: 40-47)
printf '\e[31m'       # Red foreground
printf '\e[42m'       # Green background
printf '\e[1;34m'     # Bold blue

# Bright colors (foreground: 90-97, background: 100-107)
printf '\e[91m'       # Bright red

# 256-color mode
printf '\e[38;5;%dm' 208   # Foreground: color 208 (orange)
printf '\e[48;5;%dm' 236   # Background: color 236 (dark gray)

# True color (24-bit)
printf '\e[38;2;%d;%d;%dm' 255 128 0   # Foreground RGB
printf '\e[48;2;%d;%d;%dm' 30 30 30    # Background RGB
```

### Color Utility Functions

```sh
color_fg() {
  printf '\e[38;5;%dm' "$1"
}

color_bg() {
  printf '\e[48;5;%dm' "$1"
}

rgb_fg() {
  printf '\e[38;2;%d;%d;%dm' "$1" "$2" "$3"
}

reset_color() {
  printf '\e[0m'
}
```

## Tput (Portable Terminal Control)

`tput` queries the terminfo database and outputs the correct escape sequences for the current terminal.

### Common Capabilities

```sh
tput cols             # Number of columns
tput lines            # Number of lines
tput colors           # Number of supported colors

tput cup 5 10         # Move cursor to row 5, col 10
tput home             # Move to home position
tput sc               # Save cursor
tput rc               # Restore cursor

tput clear            # Clear screen
tput el               # Clear to end of line
tput el1              # Clear to beginning of line
tput ed               # Clear to end of screen

tput bold             # Bold
tput dim              # Dim
tput smul             # Start underline
tput rmul             # End underline
tput rev              # Reverse video
tput sgr0             # Reset all attributes

tput setaf 1          # Set foreground color (0-255)
tput setab 2          # Set background color (0-255)

tput civis            # Hide cursor
tput cnorm            # Show cursor (normal)
tput smcup            # Enter alternate screen
tput rmcup            # Exit alternate screen
```

### Alternate Screen Buffer

```sh
enter_fullscreen() {
  tput smcup
  tput civis
  tput clear
}

exit_fullscreen() {
  tput rmcup
  tput cnorm
}

# Ensure cleanup on exit
trap exit_fullscreen EXIT
enter_fullscreen
```

### Feature Detection

```sh
has_color() {
  local colors
  colors=$(tput colors 2>/dev/null) || return 1
  [ "$colors" -ge 8 ]
}

has_truecolor() {
  case "$COLORTERM" in
    truecolor|24bit) return 0 ;;
  esac
  return 1
}

supports_unicode() {
  case "$LANG$LC_ALL$LC_CTYPE" in
    *UTF-8*|*utf-8*|*utf8*) return 0 ;;
  esac
  return 1
}
```

## Stty (Terminal Line Settings)

```sh
# Save current settings
saved_stty=$(stty -g)

# Restore settings
stty "$saved_stty"

# Raw mode (no echo, no line buffering)
stty raw -echo

# Read single character
read_char() {
  local old_stty
  old_stty=$(stty -g)
  stty raw -echo min 1
  local char
  char=$(dd bs=1 count=1 2>/dev/null)
  stty "$old_stty"
  printf '%s' "$char"
}

# Disable Ctrl-C (SIGINT)
stty -isig

# Disable flow control (Ctrl-S/Ctrl-Q)
stty -ixon
```

## Terminal Queries

### Window Size

```sh
# Via stty
stty size              # rows cols

# Via tput
rows=$(tput lines)
cols=$(tput cols)

# Via SIGWINCH handler
handle_resize() {
  LINES=$(tput lines)
  COLUMNS=$(tput cols)
}
trap handle_resize WINCH
```

### Cursor Position

```sh
get_cursor_pos() {
  local pos
  printf '\e[6n'
  IFS='[;' read -r -d R _ row col < /dev/tty
  printf '%d %d' "$row" "$col"
}
```

### Terminal Title

```sh
# Set title (works in most terminal emulators)
set_title() {
  printf '\e]0;%s\a' "$1"
}

# Set title with icon name separately
set_icon_title() {
  printf '\e]1;%s\a' "$1"   # Icon name
  printf '\e]2;%s\a' "$2"   # Window title
}
```

## Progress Indicators

### Spinner

```sh
spinner() {
  local pid=$1
  local frames='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
  local i=0
  while kill -0 "$pid" 2>/dev/null; do
    printf '\r%s %s' "${frames:i%${#frames}:1}" "$2"
    i=$((i + 1))
    sleep 0.1
  done
  printf '\r\e[2K'
}

long_running_task &
spinner $! "Processing..."
```

### Progress Bar

```sh
progress_bar() {
  local current=$1 total=$2 width=${3:-40}
  local pct=$((current * 100 / total))
  local filled=$((current * width / total))
  local empty=$((width - filled))

  printf '\r['
  printf '%*s' "$filled" '' | tr ' ' '#'
  printf '%*s' "$empty" '' | tr ' ' '-'
  printf '] %3d%%' "$pct"
}

for i in $(seq 1 100); do
  progress_bar "$i" 100
  sleep 0.05
done
printf '\n'
```

## OSC (Operating System Command) Sequences

```sh
# Hyperlink (supported by many modern terminals)
printf '\e]8;;https://example.com\e\\Click here\e]8;;\e\\'

# Set clipboard (OSC 52)
printf '\e]52;c;%s\a' "$(printf '%s' "text" | base64)"

# Desktop notification (iTerm2, Kitty)
printf '\e]9;%s\a' "Task complete"
```
