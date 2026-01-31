---
title: Class Diagrams
description: Class diagram syntax for classes, methods, relationships, visibility modifiers, annotations, namespaces, and generics
tags:
  [
    classDiagram,
    class,
    method,
    inheritance,
    composition,
    aggregation,
    interface,
    abstract,
    namespace,
  ]
---

# Class Diagrams

## Declaration

```mermaid
classDiagram
    class Animal {
        +String name
        +makeSound() void
    }
```

## Defining Classes

### Bracket Syntax

```mermaid
classDiagram
    class BankAccount {
        +String owner
        +BigDecimal balance
        +deposit(amount) void
        +withdraw(amount) bool
    }
```

### Colon Syntax

```mermaid
classDiagram
    class BankAccount
    BankAccount : +String owner
    BankAccount : +BigDecimal balance
    BankAccount : +deposit(amount) void
    BankAccount : +withdraw(amount) bool
```

Both syntaxes produce identical output. Bracket syntax is preferred for readability.

## Visibility Modifiers

| Symbol | Access    |
| ------ | --------- |
| `+`    | Public    |
| `-`    | Private   |
| `#`    | Protected |
| `~`    | Package   |

```mermaid
classDiagram
    class User {
        +String name
        -String passwordHash
        #int loginAttempts
        ~String internalId
        +login(password) bool
        -hashPassword(raw) String
    }
```

## Method Classifiers

| Suffix | Meaning  |
| ------ | -------- |
| `*`    | Abstract |
| `$`    | Static   |

```mermaid
classDiagram
    class Shape {
        +draw()* void
        +getDefaultColor()$ String
    }
```

## Return Types

Specify return types after the method signature.

```mermaid
classDiagram
    class Service {
        +findById(id) User
        +findAll() List~User~
        +delete(id) void
        +count()$ int
    }
```

## Generics

Use tildes to denote generic types.

```mermaid
classDiagram
    class Repository~T~ {
        +find(id) T
        +findAll() List~T~
        +save(entity) T
        +delete(id) void
    }
```

## Relationships

Eight relationship types are supported, each with distinct arrow syntax.

```mermaid
classDiagram
    Animal <|-- Dog : Inheritance
    Vehicle *-- Engine : Composition
    Library o-- Book : Aggregation
    Controller --> Service : Association
    Service ..> Repository : Dependency
    Flyable <|.. Bird : Realization
    ClassA -- ClassB : Link
    ClassC .. ClassD : Dashed Link
```

| Arrow   | Type          | Meaning                              |
| ------- | ------------- | ------------------------------------ |
| `<\|--` | Inheritance   | Child extends parent                 |
| `*--`   | Composition   | Part cannot exist without whole      |
| `o--`   | Aggregation   | Part can exist independently         |
| `-->`   | Association   | Uses or references                   |
| `..>`   | Dependency    | Depends on (weaker than association) |
| `..\|>` | Realization   | Implements interface                 |
| `--`    | Link (solid)  | General connection                   |
| `..`    | Link (dashed) | General dashed connection            |

### Bidirectional Relationships

Combine relation types for two-way relationships.

```mermaid
classDiagram
    Student "1..*" <--> "1..*" Course : enrolls
```

## Cardinality Labels

Place cardinality on either side of the relationship.

```mermaid
classDiagram
    Customer "1" --> "*" Order : places
    Order "1" --> "1..*" LineItem : contains
    LineItem "*" --> "1" Product : references
```

| Notation | Meaning     |
| -------- | ----------- |
| `1`      | Exactly one |
| `0..1`   | Zero or one |
| `1..*`   | One or more |
| `*`      | Many        |
| `n`      | N instances |
| `0..n`   | Zero to N   |

## Annotations

Mark classes with stereotypes.

```mermaid
classDiagram
    class Serializable {
        <<Interface>>
        +serialize() String
    }
    class Shape {
        <<Abstract>>
        +area()* double
        +perimeter()* double
    }
    class Color {
        <<Enumeration>>
        RED
        GREEN
        BLUE
    }
    class Logger {
        <<Service>>
        +log(message) void
    }
```

Available annotations: `<<Interface>>`, `<<Abstract>>`, `<<Service>>`, `<<Enumeration>>`.

## Namespaces

Group related classes into namespaces.

```mermaid
classDiagram
    namespace Domain {
        class User {
            +String name
            +String email
        }
        class Order {
            +int id
            +Date createdAt
        }
    }
    namespace Infrastructure {
        class UserRepository {
            +find(id) User
        }
        class OrderRepository {
            +find(id) Order
        }
    }
    UserRepository ..> User
    OrderRepository ..> Order
```

## Notes

Add notes to the diagram or to specific classes.

```mermaid
classDiagram
    class Account {
        +String id
        +deposit(amount) void
    }
    note "Domain model for banking"
    note for Account "Aggregate root"
```

## Lollipop Interfaces

Show interface implementation with a compact notation.

```mermaid
classDiagram
    class Database
    class Cache
    Storable ()-- Database
    Storable ()-- Cache
```

## Styling

Apply CSS-like styles to individual classes.

```mermaid
classDiagram
    class Important {
        +String data
    }
    class Normal {
        +String data
    }
    style Important fill:#f9f,stroke:#333,stroke-width:2px
    classDef interfaces fill:#ccf,stroke:#33f
    class Serializable:::interfaces
```

## Complete Example

```mermaid
classDiagram
    class EventEmitter {
        <<Abstract>>
        #List~Listener~ listeners
        +on(event, callback) void
        +emit(event, data) void
        +off(event, callback) void
    }
    class HttpServer {
        -int port
        -Router router
        +listen(port) void
        +close() void
    }
    class Router {
        -Map~String, Handler~ routes
        +get(path, handler) void
        +post(path, handler) void
        +match(request) Handler
    }
    class Handler {
        <<Interface>>
        +handle(request) Response*
    }
    class Middleware {
        <<Interface>>
        +process(request, next) Response*
    }

    EventEmitter <|-- HttpServer
    HttpServer *-- Router
    Router o-- Handler
    Handler <|.. Middleware
```
