---
title: Entity-Relationship Diagrams
description: ER diagram syntax for entities, attributes, relationships, cardinality using crow's foot notation
tags:
  [
    erDiagram,
    entity,
    relationship,
    cardinality,
    primary-key,
    foreign-key,
    crow-foot,
  ]
---

# Entity-Relationship Diagrams

## Declaration

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
```

## Basic Syntax

Each line follows the pattern:

```text
<entity> [<relationship> <entity> : <label>]
```

Only the first entity name is required. The relationship, second entity, and label are optional.

## Entities

Entities are automatically created when referenced. Names should use uppercase or PascalCase by convention.

```mermaid
erDiagram
    CUSTOMER {
        int id PK
        string name
        string email UK
    }
    ORDER {
        int id PK
        int customer_id FK
        date created_at
        float total
    }
    CUSTOMER ||--o{ ORDER : places
```

## Attributes

Define attributes inside entity braces with the format: `type name [key] ["comment"]`.

```mermaid
erDiagram
    PRODUCT {
        int id PK "Auto-generated"
        string name "Product display name"
        string sku UK "Stock keeping unit"
        float price
        int category_id FK
        boolean active
    }
```

| Key  | Meaning     |
| ---- | ----------- |
| `PK` | Primary Key |
| `FK` | Foreign Key |
| `UK` | Unique Key  |

Keys and comments are optional. Multiple keys can appear on a single attribute.

## Cardinality (Crow's Foot Notation)

Relationships use two-character markers on each side of the connecting line.

| Left   | Right  | Meaning      |
| ------ | ------ | ------------ |
| `\|o`  | `o\|`  | Zero or one  |
| `\|\|` | `\|\|` | Exactly one  |
| `}o`   | `o{`   | Zero or more |
| `}\|`  | `\|{`  | One or more  |

### Reading Cardinality

Read relationships from left entity to right entity:

```text
CUSTOMER ||--o{ ORDER : places
```

- Left side `||` = "exactly one" CUSTOMER
- Right side `o{` = "zero or more" ORDERS
- Reads: "One customer places zero or more orders"

### Word Aliases

Mermaid supports English aliases for cardinality markers:

```mermaid
erDiagram
    CUSTOMER one or more--one or more DELIVERY-ADDRESS : has
    CUSTOMER exactly one--zero or more ORDER : places
```

Available aliases: `"one or zero"`, `"zero or one"`, `"one or more"`, `"one or many"`, `"many(1)"`, `"1+"`, `"zero or more"`, `"zero or many"`, `"many(0)"`, `"0+"`, `"only one"`, `"exactly one"`, `"1"`.

## Relationship Lines

| Syntax | Type                     | Visual      |
| ------ | ------------------------ | ----------- |
| `--`   | Identifying (solid line) | Solid line  |
| `..`   | Non-identifying (dashed) | Dashed line |

Identifying relationships mean the child entity cannot exist without the parent.

```mermaid
erDiagram
    PERSON ||--o{ FINGERPRINT : has
    PERSON ||..o{ ADDRESS : "lives at"
```

- `PERSON ||--o{ FINGERPRINT` = identifying (fingerprint depends on person)
- `PERSON ||..o{ ADDRESS` = non-identifying (address exists independently)

## Relationship Labels

Labels describe the nature of the relationship. Wrap multi-word labels in double quotes.

```mermaid
erDiagram
    STUDENT ||--o{ ENROLLMENT : "enrolls in"
    COURSE ||--o{ ENROLLMENT : "offered through"
    PROFESSOR ||--o{ COURSE : teaches
```

## Complete Example

```mermaid
erDiagram
    USER {
        int id PK
        string username UK
        string email UK
        string password_hash
        datetime created_at
    }
    TEAM {
        int id PK
        string name
        string slug UK
    }
    TEAM_MEMBER {
        int id PK
        int user_id FK
        int team_id FK
        string role "admin, member, viewer"
    }
    PROJECT {
        int id PK
        int team_id FK
        string name
        string status "active, archived"
    }
    TASK {
        int id PK
        int project_id FK
        int assignee_id FK "Nullable"
        string title
        string priority "low, medium, high, critical"
        datetime due_date
    }
    COMMENT {
        int id PK
        int task_id FK
        int author_id FK
        text body
        datetime created_at
    }

    USER ||--o{ TEAM_MEMBER : "belongs to"
    TEAM ||--o{ TEAM_MEMBER : "has"
    TEAM ||--o{ PROJECT : owns
    PROJECT ||--o{ TASK : contains
    USER ||--o{ TASK : "assigned to"
    TASK ||--o{ COMMENT : has
    USER ||--o{ COMMENT : writes
```

## Tips

- Entity names cannot contain spaces; use underscores or PascalCase
- Attribute types are freeform strings (not validated against a type system)
- The colon before the relationship label is required
- Relationship labels are displayed on the connecting line
- Use identifying (`--`) for strong dependencies and non-identifying (`..`) for loose associations
