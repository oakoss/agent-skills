---
title: Ratatui TUI
description: Terminal user interfaces with ratatui, crossterm backend, layout system, widgets, event handling, and styling
tags: [ratatui, crossterm, tui, terminal, widgets, layout, event, styling]
---

# Ratatui TUI

## Project Setup

```toml
[dependencies]
ratatui = "0.29"
crossterm = "0.28"
color-eyre = "0.6"
```

## Application Scaffold

Ratatui uses an immediate-mode rendering model. Each frame, the entire UI is redrawn from application state.

```rust
use std::io;
use ratatui::{
    DefaultTerminal, Frame,
    crossterm::event::{self, Event, KeyCode, KeyEventKind},
};

fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;
    let terminal = ratatui::init();
    let result = run(terminal);
    ratatui::restore();
    result
}

fn run(mut terminal: DefaultTerminal) -> color_eyre::Result<()> {
    let mut app = App::default();

    loop {
        terminal.draw(|frame| app.render(frame))?;

        if let Event::Key(key) = event::read()? {
            if key.kind != KeyEventKind::Press {
                continue;
            }
            match key.code {
                KeyCode::Char('q') | KeyCode::Esc => break,
                KeyCode::Char('j') | KeyCode::Down => app.next(),
                KeyCode::Char('k') | KeyCode::Up => app.previous(),
                KeyCode::Enter => app.select(),
                _ => {}
            }
        }
    }

    Ok(())
}
```

## Layout System

Ratatui provides `Layout` to split areas into chunks using constraints.

```rust
use ratatui::{
    layout::{Constraint, Direction, Layout, Rect},
    Frame,
};

fn render(frame: &mut Frame) {
    let main_layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),    // header
            Constraint::Min(0),      // body
            Constraint::Length(1),   // footer
        ])
        .split(frame.area());

    let body_layout = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(30),  // sidebar
            Constraint::Percentage(70),  // content
        ])
        .split(main_layout[1]);

    render_header(frame, main_layout[0]);
    render_sidebar(frame, body_layout[0]);
    render_content(frame, body_layout[1]);
    render_footer(frame, main_layout[2]);
}
```

### Constraint Types

| Constraint      | Behavior                             |
| --------------- | ------------------------------------ |
| `Length(n)`     | Exact number of rows/columns         |
| `Min(n)`        | At least n, takes remaining space    |
| `Max(n)`        | At most n                            |
| `Percentage(n)` | Percentage of available space        |
| `Ratio(a, b)`   | Fraction a/b of available space      |
| `Fill(weight)`  | Fills remaining space proportionally |

## Widgets

### Block and Paragraph

```rust
use ratatui::{
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph, Wrap},
};

fn render_header(frame: &mut Frame, area: Rect) {
    let title = Line::from(vec![
        Span::styled("My App", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
        Span::raw(" v1.0"),
    ]);

    let block = Block::default()
        .title(title)
        .borders(Borders::ALL)
        .border_style(Style::default().fg(Color::Gray));

    frame.render_widget(block, area);
}

fn render_content(frame: &mut Frame, area: Rect) {
    let text = vec![
        Line::from("First line of content"),
        Line::from(vec![
            Span::raw("Mixed "),
            Span::styled("styled", Style::default().fg(Color::Yellow)),
            Span::raw(" content"),
        ]),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().title("Content").borders(Borders::ALL))
        .wrap(Wrap { trim: true });

    frame.render_widget(paragraph, area);
}
```

### List

```rust
use ratatui::widgets::{List, ListItem, ListState, HighlightSpacing};

struct App {
    items: Vec<String>,
    state: ListState,
}

impl App {
    fn render_list(&mut self, frame: &mut Frame, area: Rect) {
        let items: Vec<ListItem> = self
            .items
            .iter()
            .map(|i| ListItem::new(i.as_str()))
            .collect();

        let list = List::new(items)
            .block(Block::default().title("Items").borders(Borders::ALL))
            .highlight_style(Style::default().bg(Color::DarkGray).add_modifier(Modifier::BOLD))
            .highlight_symbol("> ")
            .highlight_spacing(HighlightSpacing::Always);

        frame.render_stateful_widget(list, area, &mut self.state);
    }

    fn next(&mut self) {
        let i = match self.state.selected() {
            Some(i) if i >= self.items.len() - 1 => 0,
            Some(i) => i + 1,
            None => 0,
        };
        self.state.select(Some(i));
    }

    fn previous(&mut self) {
        let i = match self.state.selected() {
            Some(0) | None => self.items.len() - 1,
            Some(i) => i - 1,
        };
        self.state.select(Some(i));
    }
}
```

### Table

```rust
use ratatui::widgets::{Cell, Row, Table, TableState};

fn render_table(frame: &mut Frame, area: Rect, state: &mut TableState) {
    let header = Row::new(vec![
        Cell::from("Name").style(Style::default().fg(Color::Yellow)),
        Cell::from("Email"),
        Cell::from("Status"),
    ])
    .height(1)
    .bottom_margin(1);

    let rows = vec![
        Row::new(vec!["Alice", "alice@example.com", "Active"]),
        Row::new(vec!["Bob", "bob@example.com", "Inactive"]),
    ];

    let table = Table::new(rows, [
        Constraint::Percentage(30),
        Constraint::Percentage(50),
        Constraint::Percentage(20),
    ])
    .header(header)
    .block(Block::default().title("Users").borders(Borders::ALL))
    .highlight_style(Style::default().bg(Color::DarkGray));

    frame.render_stateful_widget(table, area, state);
}
```

### Gauge and Sparkline

```rust
use ratatui::widgets::{Gauge, Sparkline};

fn render_progress(frame: &mut Frame, area: Rect, progress: f64) {
    let gauge = Gauge::default()
        .block(Block::default().title("Progress").borders(Borders::ALL))
        .gauge_style(Style::default().fg(Color::Green))
        .percent((progress * 100.0) as u16)
        .label(format!("{:.1}%", progress * 100.0));

    frame.render_widget(gauge, area);
}

fn render_sparkline(frame: &mut Frame, area: Rect, data: &[u64]) {
    let sparkline = Sparkline::default()
        .block(Block::default().title("Activity").borders(Borders::ALL))
        .data(data)
        .style(Style::default().fg(Color::Cyan));

    frame.render_widget(sparkline, area);
}
```

## Event Handling with Polling

For non-blocking event handling, use `event::poll` with a timeout.

```rust
use std::time::{Duration, Instant};
use crossterm::event::{self, Event, KeyCode, KeyEventKind};

fn run_with_tick(mut terminal: DefaultTerminal) -> color_eyre::Result<()> {
    let mut app = App::default();
    let tick_rate = Duration::from_millis(250);
    let mut last_tick = Instant::now();

    loop {
        terminal.draw(|frame| app.render(frame))?;

        let timeout = tick_rate.saturating_sub(last_tick.elapsed());
        if event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                if key.kind == KeyEventKind::Press {
                    match key.code {
                        KeyCode::Char('q') => break,
                        _ => app.handle_key(key.code),
                    }
                }
            }
        }

        if last_tick.elapsed() >= tick_rate {
            app.on_tick();
            last_tick = Instant::now();
        }
    }

    Ok(())
}
```

## Styling

```rust
use ratatui::style::{Color, Modifier, Style, Stylize};

let style = Style::default()
    .fg(Color::Cyan)
    .bg(Color::Black)
    .add_modifier(Modifier::BOLD | Modifier::ITALIC);

// Shorthand with Stylize trait
let span = Span::raw("hello").cyan().bold();
let line = Line::from("status").green().on_dark_gray();
```

### Color Palette

| Color                       | Use               |
| --------------------------- | ----------------- |
| `Color::Reset`              | Terminal default  |
| `Color::Rgb(r, g, b)`       | True color        |
| `Color::Indexed(n)`         | 256-color palette |
| `Color::Red`, `Green`, etc. | Basic 16 colors   |
