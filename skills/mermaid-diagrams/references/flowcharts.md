---
title: Flowcharts
description: Flowchart syntax including node shapes, edge types, subgraphs, directions, styling, and interactions
tags: [flowchart, nodes, edges, subgraph, styling, classDef, direction, links]
---

# Flowcharts

## Declaration and Direction

Start with `flowchart` followed by a direction keyword.

```mermaid
flowchart LR
    A --> B --> C
```

| Direction | Meaning         |
| --------- | --------------- |
| `TB`      | Top to bottom   |
| `TD`      | Top-down (= TB) |
| `BT`      | Bottom to top   |
| `RL`      | Right to left   |
| `LR`      | Left to right   |

## Node Shapes

Nodes are defined by their ID and shape delimiters. Text inside the delimiters becomes the label.

```mermaid
flowchart TD
    A[Rectangle]
    B(Rounded)
    C([Stadium])
    D[[Subroutine]]
    E[(Cylinder)]
    F((Circle))
    G>Asymmetric]
    H{Diamond}
    I{{Hexagon}}
    J[/Parallelogram/]
    K[\Parallelogram Alt\]
    L[/Trapezoid\]
    M[\Trapezoid Alt/]
    N(((Double Circle)))
```

### Extended Shapes (v11.3.0+)

Use the `@{ shape: name }` syntax for additional shapes.

```mermaid
flowchart LR
    A@{ shape: rect, label: "Rectangle" }
    B@{ shape: diamond, label: "Decision" }
    C@{ shape: stadium, label: "Stadium" }
    D@{ shape: cylinder, label: "Database" }
    E@{ shape: document, label: "Document" }
```

## Edge Types

Edges connect nodes with various line styles and terminators.

```mermaid
flowchart LR
    A --> B
    C --- D
    E -.- F
    G === H
    I -.-> J
    K ==> L
    M o--o N
    N x--x O
```

| Syntax | Description         |
| ------ | ------------------- |
| `-->`  | Arrow               |
| `---`  | Open link           |
| `-.-`  | Dotted link         |
| `===`  | Thick link          |
| `-.->` | Dotted arrow        |
| `==>`  | Thick arrow         |
| `o--o` | Circle endpoints    |
| `x--x` | Cross endpoints     |
| `<-->` | Bidirectional arrow |

### Edge Labels

Add text to edges using pipe syntax or inline text.

```mermaid
flowchart LR
    A -->|Yes| B
    A -->|No| C
    D -- "Edge label" --> E
```

### Multi-length Edges

Add extra characters to increase edge length.

```mermaid
flowchart TD
    A --> B
    A ---> C
    A ----> D
```

## Subgraphs

Group related nodes inside subgraphs. Subgraphs can be nested and can have their own direction.

```mermaid
flowchart TB
    c1 --> a2
    subgraph one [First Group]
        a1 --> a2
    end
    subgraph two [Second Group]
        direction LR
        b1 --> b2
    end
    subgraph three [Third Group]
        c1 --> c2
    end
    one --> two
```

Key rules:

- Subgraph IDs are used for edges between subgraphs
- Use `direction` inside a subgraph to override parent direction
- If a subgraph node links to the outside, direction is inherited from parent
- Subgraphs can be nested arbitrarily deep

## Styling

### Class Definitions

Define reusable styles with `classDef` and apply them with `class` or the `:::` shorthand.

```mermaid
flowchart LR
    A:::success --> B:::error
    classDef success fill:#d4edda,stroke:#28a745,color:#155724
    classDef error fill:#f8d7da,stroke:#dc3545,color:#721c24
```

### Inline Styles

Apply styles directly to specific nodes or links.

```mermaid
flowchart LR
    A --> B --> C
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#33f
    linkStyle 0 stroke:#ff3,stroke-width:4px
    linkStyle 1 stroke:#3f3,stroke-width:2px
```

The `linkStyle` index corresponds to the order edges appear in the definition (0-based).

### Default Styling

Apply a style to all nodes using the `default` class.

```mermaid
flowchart LR
    A --> B --> C
    classDef default fill:#f0f0f0,stroke:#333
```

## Click Interactions

Bind click events to nodes for callbacks or navigation.

```mermaid
flowchart LR
    A --> B --> C
    click A "https://example.com" "Open docs" _blank
    click B callback "Trigger action"
```

Supported targets: `_self`, `_blank`, `_parent`, `_top`.

## Markdown Strings

Use double quotes with backticks for rich text formatting in labels.

```mermaid
flowchart LR
    A["`**Bold** and *italic* text`"] --> B["`Line one
Line two`"]
```

Markdown strings support bold, italics, and automatic text wrapping.

## Comments

Add comments with `%%` at the start of a line.

```mermaid
flowchart LR
    %% This is a comment
    A --> B
```

## Complete Example

```mermaid
flowchart TD
    Start([Start]) --> CheckAuth{Authenticated?}
    CheckAuth -->|Yes| Dashboard[Dashboard]
    CheckAuth -->|No| Login[Login Page]
    Login --> Validate{Valid Credentials?}
    Validate -->|Yes| Dashboard
    Validate -->|No| Login

    subgraph auth [Authentication Flow]
        Login
        Validate
    end

    Dashboard --> Logout([Logout])
    Logout --> Login

    classDef decision fill:#ffeaa7,stroke:#fdcb6e
    classDef page fill:#dfe6e9,stroke:#b2bec3
    classDef action fill:#55efc4,stroke:#00b894
    class CheckAuth,Validate decision
    class Dashboard,Login page
    class Start,Logout action
```
