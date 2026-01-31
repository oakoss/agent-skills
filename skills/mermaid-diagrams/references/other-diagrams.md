---
title: Other Diagrams
description: Gantt charts, pie charts, mindmaps, state diagrams, and git graphs in Mermaid
tags: [gantt, pie, mindmap, state, stateDiagram, gitGraph, timeline]
---

# Other Diagrams

## Gantt Charts

Gantt charts visualize project schedules with tasks, durations, and dependencies.

### Basic Structure

```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    excludes weekends

    section Planning
    Requirements     :done, req, 2024-01-01, 5d
    Design           :active, des, after req, 10d

    section Development
    Backend API      :dev1, after des, 15d
    Frontend UI      :dev2, after des, 12d
    Integration      :dev3, after dev1, 5d

    section Release
    Testing          :test, after dev3, 7d
    Launch           :milestone, launch, after test, 0d
```

### Task Modifiers

| Modifier    | Effect                    |
| ----------- | ------------------------- |
| `done`      | Marks task as completed   |
| `active`    | Marks task as in progress |
| `crit`      | Marks as critical path    |
| `milestone` | Zero-duration marker      |

### Date Formats

Set with `dateFormat`. Common formats: `YYYY-MM-DD`, `DD-MM-YYYY`, `YYYY-MM-DDTHH:mm`.

### Duration Syntax

Tasks accept absolute dates or relative durations.

```mermaid
gantt
    dateFormat YYYY-MM-DD
    section Durations
    Five days        :a, 2024-01-01, 5d
    24 hours         :b, after a, 24h
    One week         :c, after b, 1w
    Until date       :d, after c, 2024-02-15
```

### Dependencies

Use `after <task-id>` to chain tasks.

```mermaid
gantt
    dateFormat YYYY-MM-DD
    A :a, 2024-01-01, 3d
    B :b, after a, 2d
    C :c, after a, 4d
    D :d, after b c, 2d
```

Task D starts after both B and C complete.

## Pie Charts

Simple proportional data visualization.

```mermaid
pie title Revenue by Product
    "Product A" : 45
    "Product B" : 30
    "Product C" : 15
    "Product D" : 10
```

### Show Data Values

Display raw values alongside percentages.

```mermaid
pie showData
    title Browser Market Share
    "Chrome" : 65
    "Safari" : 19
    "Firefox" : 8
    "Edge" : 5
    "Other" : 3
```

Values are numeric (integers or decimals). Labels must be in double quotes.

## Mindmaps

Hierarchical diagrams using indentation for parent-child relationships.

### Basic Structure

```mermaid
mindmap
    root((Project))
        Frontend
            React
            TypeScript
            TailwindCSS
        Backend
            Node.js
            PostgreSQL
            Redis
        Infrastructure
            AWS
            Docker
            CI/CD
```

### Node Shapes

```mermaid
mindmap
    root
        Default shape
        [Square]
        (Rounded)
        ((Circle))
        ))Cloud((
        {{Hexagon}}
```

| Syntax     | Shape          |
| ---------- | -------------- |
| Plain text | Default        |
| `[text]`   | Square         |
| `(text)`   | Rounded square |
| `((text))` | Circle         |
| `))text((` | Cloud          |
| `{{text}}` | Hexagon        |

### Icons and Formatting

```mermaid
mindmap
    root((Central Topic))
        ::icon(fa fa-book)
        **Bold text**
        *Italic text*
        A longer label that wraps
```

Icons use Font Awesome or Material Design class names with `::icon(class)`.

## State Diagrams

Model state machines with transitions, composite states, and concurrency.

### Basic States and Transitions

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : Submit
    Processing --> Success : Complete
    Processing --> Error : Fail
    Error --> Idle : Retry
    Success --> [*]
```

`[*]` represents the start state (when targeted) or end state (when sourced).

### State Descriptions

```mermaid
stateDiagram-v2
    state "Waiting for input" as Waiting
    state "Processing request" as Processing
    [*] --> Waiting
    Waiting --> Processing : Receive
    Processing --> Waiting : Done
```

### Composite States

Nest states inside parent states.

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Idle
        Idle --> Running : start
        Running --> Idle : stop
    }

    Active --> Inactive : disable
    Inactive --> Active : enable
```

### Choice

Branch transitions based on conditions.

```mermaid
stateDiagram-v2
    state check <<choice>>
    [*] --> check
    check --> Approved : if valid
    check --> Rejected : if invalid
    Approved --> [*]
    Rejected --> [*]
```

### Forks and Joins

Model parallel execution paths.

```mermaid
stateDiagram-v2
    state fork_state <<fork>>
    state join_state <<join>>
    [*] --> fork_state
    fork_state --> TaskA
    fork_state --> TaskB
    TaskA --> join_state
    TaskB --> join_state
    join_state --> Done
    Done --> [*]
```

### Concurrency

Show parallel regions within a state using `--`.

```mermaid
stateDiagram-v2
    [*] --> Active
    state Active {
        [*] --> ProcessA
        --
        [*] --> ProcessB
    }
    Active --> [*]
```

### Notes

```mermaid
stateDiagram-v2
    [*] --> Active
    Active --> Inactive
    note right of Active
        This state handles
        all user interactions
    end note
    note left of Inactive : System is paused
```

## Git Graphs

Visualize branching, merging, and commit history.

### Basic Commands

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
```

### Commit Options

```mermaid
gitGraph
    commit id: "init"
    commit id: "feat-1" tag: "v1.0.0"
    branch feature
    commit id: "wip"
    commit id: "done" type: HIGHLIGHT
    checkout main
    merge feature id: "merge-feat" tag: "v1.1.0"
    commit id: "hotfix" type: REVERSE
```

| Option | Values                             |
| ------ | ---------------------------------- |
| `id`   | Custom commit identifier (quoted)  |
| `tag`  | Label displayed on commit (quoted) |
| `type` | `NORMAL`, `REVERSE`, `HIGHLIGHT`   |

### Cherry-pick

```mermaid
gitGraph
    commit id: "base"
    branch feature
    commit id: "important-fix"
    checkout main
    cherry-pick id: "important-fix"
    commit
```

The cherry-picked commit must have a custom `id` and must exist on a different branch.

### Branch Ordering

Control the visual order of branches.

```mermaid
gitGraph
    commit
    branch hotfix order: 1
    branch feature order: 2
    checkout feature
    commit
    checkout hotfix
    commit
    checkout main
    merge hotfix
    merge feature
```

Lower `order` values appear closer to main.

### Orientation

```mermaid
gitGraph TB:
    commit
    branch develop
    commit
    checkout main
    merge develop
```

Orientations: `LR` (default, left-to-right), `TB` (top-to-bottom), `BT` (bottom-to-top).

## Configuration

All diagram types support frontmatter configuration.

```mermaid
---
config:
  theme: forest
---
flowchart LR
    A --> B
```

Available themes: `default`, `neutral`, `dark`, `forest`, `base`.
