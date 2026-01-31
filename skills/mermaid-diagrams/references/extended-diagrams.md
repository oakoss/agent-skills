---
title: Extended Diagrams
description: Architecture, block, timeline, Sankey, XY chart, quadrant, kanban, packet, requirement, and C4 diagram syntax
tags:
  [
    architecture,
    block,
    timeline,
    sankey,
    xychart,
    quadrant,
    kanban,
    packet,
    requirement,
    c4,
  ]
---

# Extended Diagrams

Mermaid v11 introduced several diagram types beyond the core set. Many use `-beta` suffixes in their declarations.

## Architecture Diagrams

Visualize system architecture with services, groups, and directional edges.

```mermaid
architecture-beta
    group api(cloud)[API]

    service db(database)[Database] in api
    service server(server)[Server] in api
    service disk(disk)[Storage] in api

    db:R -- L:server
    server:R -- L:disk
```

Key syntax:

- `group name(icon)[Label]` -- define a group with an icon
- `service name(icon)[Label] in group` -- place a service in a group
- `service:PORT -- PORT:service` -- connect with directional edges
- Ports: `T` (top), `B` (bottom), `L` (left), `R` (right)
- Icons: `cloud`, `database`, `server`, `disk`, `internet`

## Block Diagrams

Grid-based layout with columns, block arrows, and nested blocks.

```mermaid
block-beta
    columns 3
    Frontend blockArrowId6<[" "]>(right) Backend
    space:2 down<[" "]>(down)
    Disk left<[" "]>(left) Database[("Database")]
```

Key syntax:

- `columns N` -- set grid column count
- `space` or `space:N` -- insert empty cells
- `id<["label"]>(direction)` -- block arrow (up, down, left, right)
- Standard node shapes from flowcharts work inside blocks

## Timeline Diagrams

Display chronological events grouped by time periods.

```mermaid
timeline
    title Project History
    section 2023
        Q1 : Requirements gathering
           : Team formation
        Q2 : MVP development
    section 2024
        Q1 : Beta launch
        Q2 : General availability
```

Key syntax:

- `title` -- optional diagram title
- `section Name` -- group events by time period
- Indent events under their time period
- Multiple events per period separated by `:` on new lines

## Sankey Diagrams

Visualize flow quantities between nodes using a CSV-like format.

```mermaid
sankey-beta

Agricultural "waste",Bio-conversion,124.729
Bio-conversion,Liquid,0.597
Bio-conversion,Losses,26.862
Bio-conversion,Solid,280.322
Bio-conversion,Gas,81.144
```

Key syntax:

- Each line: `source,target,value`
- Values determine the width of flow connections
- Nodes are created automatically from source/target names
- Wrap node names in quotes if they contain commas

## XY Charts

Bar and line charts with labeled axes.

```mermaid
xychart-beta
    title "Monthly Revenue"
    x-axis [Jan, Feb, Mar, Apr, May, Jun]
    y-axis "Revenue (USD)" 4000 --> 11000
    bar [5000, 6000, 7500, 8200, 9800, 10500]
    line [5000, 6000, 7000, 8000, 9000, 10000]
```

Key syntax:

- `x-axis [labels]` or `x-axis "Label" min --> max`
- `y-axis "Label" min --> max`
- `bar [values]` -- bar chart data
- `line [values]` -- line chart data
- Multiple `bar` and `line` series supported

## Quadrant Charts

Four-quadrant plots for comparative analysis.

```mermaid
quadrantChart
    title Technology Radar
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Do First
    quadrant-2 Schedule
    quadrant-3 Delegate
    quadrant-4 Eliminate
    Component A: [0.8, 0.9]
    Component B: [0.3, 0.7]
    Component C: [0.6, 0.2]
    Component D: [0.2, 0.3]
```

Key syntax:

- `x-axis` and `y-axis` define axis labels with arrows for direction
- `quadrant-1` through `quadrant-4` label each quadrant
- Data points: `Label: [x, y]` with values 0.0 to 1.0

## Kanban Diagrams

Kanban boards with columns and task cards.

```mermaid
kanban
    Todo
        [Design API schema]
        [Write migration scripts]
    In Progress
        [Implement auth service]
    Done
        [Set up CI pipeline]
```

Key syntax:

- Column names at top indentation level
- Task cards indented under columns: `[Task title]`
- Task metadata: `id[Title]@{ assigned: 'name', priority: 'High', ticket: 'PROJ-123' }`
- Configure ticket URLs: `config.kanban.ticketBaseUrl`

## Packet Diagrams

Visualize network packet structures with bit-range fields.

```mermaid
packet-beta
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
    64-95: "Acknowledgment Number"
    96-99: "Data Offset"
    100-105: "Reserved"
    106-111: "Flags"
    112-127: "Window Size"
```

Key syntax:

- `start-end: "Label"` -- define a field spanning bit range
- `+N: "Label"` -- auto-increment N bits from previous position
- Default row width is 32 bits (configurable)

## Requirement Diagrams

Model requirements with elements and verification relationships.

```mermaid
requirementDiagram
    requirement Login Feature {
        id: 1
        text: Users must authenticate via OAuth2
        risk: high
        verifymethod: test
    }

    element Auth Service {
        type: microservice
    }

    Auth Service - satisfies -> Login Feature
```

Requirement types: `requirement`, `functionalRequirement`, `performanceRequirement`, `interfaceRequirement`, `physicalRequirement`, `designConstraint`.

Relationships: `contains`, `copies`, `derives`, `satisfies`, `verifies`, `refines`, `traces`.

## C4 Diagrams

Model software architecture using the C4 model at four levels.

```mermaid
C4Context
    title System Context Diagram
    Person(user, "User", "A customer")
    System(app, "Web Application", "The main system")
    System_Ext(email, "Email System", "Sends notifications")

    Rel(user, app, "Uses", "HTTPS")
    Rel(app, email, "Sends emails", "SMTP")
```

Diagram levels:

- `C4Context` -- system context (people and systems)
- `C4Container` -- containers within a system
- `C4Component` -- components within a container
- `C4Deployment` -- deployment nodes and infrastructure

Key elements:

- `Person(id, "Name", "Description")`
- `System(id, "Name", "Description")` / `System_Ext` for external
- `Container(id, "Name", "Tech", "Description")` / `ContainerDb`
- `Component(id, "Name", "Tech", "Description")`
- `Container_Boundary(id, "Label") { ... }` for grouping
- `Rel(from, to, "Label", "Tech")` for relationships
