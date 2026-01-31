---
title: Sequence Diagrams
description: Sequence diagram syntax for participants, messages, activations, loops, alt/opt/par, notes, and grouping
tags:
  [
    sequence,
    participant,
    actor,
    message,
    activation,
    loop,
    alt,
    opt,
    par,
    notes,
  ]
---

# Sequence Diagrams

## Declaration

```mermaid
sequenceDiagram
    Alice->>Bob: Hello Bob
    Bob-->>Alice: Hi Alice
```

## Participants and Actors

Declare participants explicitly to control ordering, or let them appear implicitly.

```mermaid
sequenceDiagram
    participant A as Auth Service
    participant B as Backend API
    actor U as User
    U->>A: Login request
    A->>B: Validate token
    B-->>A: Token valid
    A-->>U: Session created
```

| Keyword       | Rendering        |
| ------------- | ---------------- |
| `participant` | Rectangle box    |
| `actor`       | Stick figure     |
| `boundary`    | Boundary box     |
| `control`     | Control circle   |
| `entity`      | Entity underline |
| `database`    | Database icon    |
| `collections` | Stack icon       |
| `queue`       | Queue icon       |

## Message Arrow Types

| Arrow    | Description                |
| -------- | -------------------------- |
| `->`     | Solid line, no arrowhead   |
| `-->`    | Dotted line, no arrowhead  |
| `->>`    | Solid line with arrowhead  |
| `-->>`   | Dotted line with arrowhead |
| `<<->>`  | Solid bidirectional        |
| `<<-->>` | Dotted bidirectional       |
| `-x`     | Solid line with cross      |
| `--x`    | Dotted line with cross     |
| `-)`     | Solid async arrow          |
| `--)`    | Dotted async arrow         |

## Activations

Show when a participant is actively processing. Use explicit keywords or shorthand notation.

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    C->>+S: Request
    S->>+S: Process
    S->>-S: Done processing
    S-->>-C: Response
```

The `+` suffix activates and `-` deactivates. Multiple activations can stack on the same participant.

Explicit form:

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    C->>S: Request
    activate S
    S-->>C: Response
    deactivate S
```

## Loops

Repeat a block of messages.

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    C->>S: Subscribe
    loop Every 30 seconds
        S-->>C: Heartbeat
    end
```

## Alt / Else (Conditional)

Model branching logic with alternative paths.

```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    U->>S: Login
    alt Valid credentials
        S-->>U: 200 OK
    else Invalid credentials
        S-->>U: 401 Unauthorized
    end
```

## Opt (Optional)

Model an optional interaction that may or may not occur.

```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    U->>S: Request data
    opt Cache available
        S-->>U: Cached response
    end
    S-->>U: Fresh response
```

## Par (Parallel)

Show concurrent interactions.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Service A
    participant B as Service B
    par Request to A
        C->>A: Fetch users
    and Request to B
        C->>B: Fetch orders
    end
    A-->>C: Users
    B-->>C: Orders
```

Nested `par` blocks are supported for deeper concurrency.

## Critical Regions

Mark interactions that must succeed, with fallback options.

```mermaid
sequenceDiagram
    participant C as Client
    participant DB as Database
    critical Establish connection
        C->>DB: Connect
    option Connection timeout
        C->>C: Retry with backoff
    option Connection refused
        C->>C: Use fallback cache
    end
```

## Break

Exit the sequence flow when a condition is met.

```mermaid
sequenceDiagram
    participant C as Consumer
    participant Q as Queue
    C->>Q: Poll message
    break No messages available
        Q-->>C: Empty response
    end
    Q-->>C: Message payload
```

## Notes

Add annotations to specific participants.

```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello
    Note right of B: Thinking...
    Note left of A: Waiting
    Note over A,B: Handshake complete
    B-->>A: Hi there
```

Positions: `right of`, `left of`, `over` (single or range with comma).

## Background Highlighting

Use `rect` to highlight a region of the diagram.

```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    rect rgb(200, 220, 255)
        A->>B: Request inside highlight
        B-->>A: Response inside highlight
    end
```

## Participant Grouping

Group participants into labeled boxes.

```mermaid
sequenceDiagram
    box Blue Frontend
        participant U as User
        participant UI as Browser
    end
    box Green Backend
        participant API as API Server
        participant DB as Database
    end
    U->>UI: Click button
    UI->>API: HTTP request
    API->>DB: Query
    DB-->>API: Results
    API-->>UI: JSON response
    UI-->>U: Render data
```

## Sequence Numbers

Enable automatic numbering on all messages.

```mermaid
sequenceDiagram
    autonumber
    participant A as Alice
    participant B as Bob
    A->>B: First message
    B-->>A: Second message
    A->>B: Third message
```

## Create and Destroy

Dynamically create or destroy participants during the sequence.

```mermaid
sequenceDiagram
    participant A as Alice
    A->>Bob: Hello
    create participant C as Charlie
    Bob->>C: Introduce Alice
    destroy C
    C->>Bob: Goodbye
```

## Actor Menus

Add links to participant menus for interactive diagrams.

```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    link A: Dashboard @ https://example.com/dashboard
    link B: Profile @ https://example.com/profile
    A->>B: Check your profile
```

## Complete Example

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant FE as Frontend
    participant GW as API Gateway
    participant Auth as Auth Service
    participant DB as Database

    U->>FE: Submit login form
    FE->>+GW: POST /auth/login
    GW->>+Auth: Validate credentials

    alt Valid credentials
        Auth->>+DB: Lookup user
        DB-->>-Auth: User record
        Auth-->>-GW: JWT token
        GW-->>-FE: 200 OK + token
        FE-->>U: Redirect to dashboard
    else Invalid credentials
        Auth-->>GW: Authentication failed
        GW-->>FE: 401 Unauthorized
        FE-->>U: Show error message
    end
```
