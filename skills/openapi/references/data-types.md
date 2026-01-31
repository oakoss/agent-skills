---
title: Data Types
description: Schema types, formats, oneOf/anyOf/allOf composition, discriminators, and nullable handling in OpenAPI 3.1
tags:
  [types, formats, oneOf, anyOf, allOf, discriminator, nullable, enum, pattern]
---

# Data Types

## Primitive Types

OpenAPI 3.1 supports JSON Schema Draft 2020-12 types:

```yaml
type: string
type: number
type: integer
type: boolean
type: array
type: object
type: 'null'
```

In 3.1, `type` can be an array to express union types:

```yaml
type: ['string', 'null']
```

## String Formats

```yaml
properties:
  id:
    type: string
    format: uuid
  email:
    type: string
    format: email
  website:
    type: string
    format: uri
  created:
    type: string
    format: date-time
  birthday:
    type: string
    format: date
  duration:
    type: string
    format: duration
  ip:
    type: string
    format: ipv4
  password:
    type: string
    format: password
```

## Number Constraints

```yaml
properties:
  age:
    type: integer
    minimum: 0
    maximum: 150
  price:
    type: number
    minimum: 0
    exclusiveMinimum: 0
    multipleOf: 0.01
  quantity:
    type: integer
    minimum: 1
    maximum: 1000
```

In OpenAPI 3.1, `exclusiveMinimum` and `exclusiveMaximum` are numbers (not booleans as in 3.0):

```yaml
properties:
  score:
    type: number
    exclusiveMinimum: 0
    exclusiveMaximum: 100
```

## String Constraints

```yaml
properties:
  username:
    type: string
    minLength: 3
    maxLength: 32
    pattern: '^[a-zA-Z0-9_]+$'
  slug:
    type: string
    pattern: '^[a-z0-9]+(?:-[a-z0-9]+)*$'
```

## Enums and Constants

```yaml
properties:
  status:
    type: string
    enum: [active, inactive, suspended]
  version:
    type: string
    const: '1.0'
```

## Arrays

```yaml
properties:
  tags:
    type: array
    items:
      type: string
    minItems: 1
    maxItems: 10
    uniqueItems: true
  matrix:
    type: array
    items:
      type: array
      items:
        type: number
    minItems: 3
    maxItems: 3
  coordinates:
    type: array
    prefixItems:
      - type: number
      - type: number
    items: false
    minItems: 2
    maxItems: 2
```

## Objects

```yaml
properties:
  metadata:
    type: object
    properties:
      key:
        type: string
    required: [key]
    additionalProperties: false
  tags:
    type: object
    additionalProperties:
      type: string
    minProperties: 1
    maxProperties: 20
  config:
    type: object
    propertyNames:
      pattern: '^[a-z][a-zA-Z0-9]*$'
    additionalProperties:
      type: string
```

## Nullable Fields (3.1)

OpenAPI 3.1 removed `nullable: true`. Use type arrays instead:

```yaml
properties:
  middleName:
    type: ['string', 'null']
  deletedAt:
    type: ['string', 'null']
    format: date-time
  bio:
    oneOf:
      - type: string
        maxLength: 500
      - type: 'null'
```

## Composition: allOf

Combine schemas (intersection). All subschemas must validate:

```yaml
components:
  schemas:
    BaseEntity:
      type: object
      properties:
        id:
          type: string
          format: uuid
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time
      required: [id, createdAt, updatedAt]

    User:
      allOf:
        - $ref: '#/components/schemas/BaseEntity'
        - type: object
          properties:
            name:
              type: string
            email:
              type: string
              format: email
          required: [name, email]
```

## Composition: oneOf

Exactly one subschema must validate (exclusive union):

```yaml
components:
  schemas:
    PaymentMethod:
      oneOf:
        - $ref: '#/components/schemas/CreditCard'
        - $ref: '#/components/schemas/BankTransfer'
        - $ref: '#/components/schemas/DigitalWallet'

    CreditCard:
      type: object
      properties:
        type:
          type: string
          const: credit_card
        cardNumber:
          type: string
        expiryMonth:
          type: integer
        expiryYear:
          type: integer
      required: [type, cardNumber, expiryMonth, expiryYear]

    BankTransfer:
      type: object
      properties:
        type:
          type: string
          const: bank_transfer
        accountNumber:
          type: string
        routingNumber:
          type: string
      required: [type, accountNumber, routingNumber]

    DigitalWallet:
      type: object
      properties:
        type:
          type: string
          const: digital_wallet
        provider:
          type: string
          enum: [apple_pay, google_pay]
        token:
          type: string
      required: [type, provider, token]
```

## Composition: anyOf

At least one subschema must validate (inclusive union). Use when the value can match one or more schemas:

```yaml
components:
  schemas:
    SearchFilter:
      anyOf:
        - type: object
          properties:
            name:
              type: string
          required: [name]
        - type: object
          properties:
            email:
              type: string
              format: email
          required: [email]
```

## Discriminator

Hints for code generators to select the correct schema branch. Only valid with `oneOf`, `anyOf`, or `allOf`:

```yaml
components:
  schemas:
    Event:
      oneOf:
        - $ref: '#/components/schemas/UserCreatedEvent'
        - $ref: '#/components/schemas/OrderPlacedEvent'
        - $ref: '#/components/schemas/PaymentProcessedEvent'
      discriminator:
        propertyName: eventType
        mapping:
          user.created: '#/components/schemas/UserCreatedEvent'
          order.placed: '#/components/schemas/OrderPlacedEvent'
          payment.processed: '#/components/schemas/PaymentProcessedEvent'

    UserCreatedEvent:
      type: object
      properties:
        eventType:
          type: string
        userId:
          type: string
      required: [eventType, userId]

    OrderPlacedEvent:
      type: object
      properties:
        eventType:
          type: string
        orderId:
          type: string
        total:
          type: number
      required: [eventType, orderId, total]

    PaymentProcessedEvent:
      type: object
      properties:
        eventType:
          type: string
        paymentId:
          type: string
        amount:
          type: number
      required: [eventType, paymentId, amount]
```

Every schema in the `oneOf`/`anyOf` must include the discriminator property. Without explicit `mapping`, schema names are used as discriminator values.

## readOnly and writeOnly

Control which properties appear in requests vs responses:

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
        password:
          type: string
          format: password
          writeOnly: true
        name:
          type: string
      required: [id, name]
```

- `readOnly: true` — included in responses, excluded from requests
- `writeOnly: true` — included in requests, excluded from responses

## Default Values

```yaml
properties:
  role:
    type: string
    enum: [admin, member, viewer]
    default: member
  isActive:
    type: boolean
    default: true
  pageSize:
    type: integer
    default: 20
    minimum: 1
    maximum: 100
```
