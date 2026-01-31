---
title: Schema Design
description: Paths, operations, request/response bodies, parameters, components, and $ref patterns for OpenAPI 3.1
tags:
  [
    paths,
    operations,
    parameters,
    request-body,
    response,
    components,
    ref,
    schema,
  ]
---

# Schema Design

## Document Structure

Every OpenAPI 3.1 document requires three top-level fields:

```yaml
openapi: '3.1.0'
info:
  title: My API
  version: 1.0.0
  description: A sample API
  contact:
    name: API Support
    email: support@example.com
  license:
    name: MIT
paths: {}
```

Optional top-level fields: `servers`, `components`, `security`, `tags`, `externalDocs`, `webhooks`.

## Servers

Define base URLs for different environments:

```yaml
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging
  - url: http://localhost:3000/v1
    description: Local development
```

Server URLs support variables:

```yaml
servers:
  - url: https://{environment}.example.com/v1
    variables:
      environment:
        default: api
        enum: [api, staging, sandbox]
```

## Paths and Operations

Each path defines operations (HTTP methods):

```yaml
paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
      tags: [users]
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/LimitParam'
      responses:
        '200':
          description: Paginated list of users
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
    post:
      operationId: createUser
      summary: Create a new user
      tags: [users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '422':
          $ref: '#/components/responses/ValidationError'

  /users/{userId}:
    get:
      operationId: getUser
      summary: Get a user by ID
      tags: [users]
      parameters:
        - $ref: '#/components/parameters/UserIdParam'
      responses:
        '200':
          description: User details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'
```

## Parameters

Four parameter locations: `path`, `query`, `header`, `cookie`.

```yaml
components:
  parameters:
    UserIdParam:
      name: userId
      in: path
      required: true
      description: Unique user identifier
      schema:
        type: string
        format: uuid

    PageParam:
      name: page
      in: query
      required: false
      schema:
        type: integer
        minimum: 1
        default: 1

    LimitParam:
      name: limit
      in: query
      required: false
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20

    ApiVersionHeader:
      name: X-API-Version
      in: header
      required: false
      schema:
        type: string
        default: '2024-01'
```

Path parameters must always have `required: true`. Query parameters with array values use `style` and `explode`:

```yaml
parameters:
  - name: tags
    in: query
    schema:
      type: array
      items:
        type: string
    style: form
    explode: true
```

## Request Bodies

```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/CreateUserRequest'
      examples:
        basic:
          summary: Basic user
          value:
            name: Jane Doe
            email: jane@example.com
    multipart/form-data:
      schema:
        type: object
        properties:
          avatar:
            type: string
            format: binary
          name:
            type: string
        required: [name]
```

## Responses

Every operation needs at least one response. Define reusable responses in components:

```yaml
components:
  responses:
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    ValidationError:
      description: Validation failed
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ValidationError'
```

Response headers:

```yaml
responses:
  '200':
    description: Success
    headers:
      X-Request-Id:
        schema:
          type: string
          format: uuid
      X-Rate-Limit-Remaining:
        schema:
          type: integer
```

## Components and $ref

Extract reusable elements into `components`:

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          minLength: 1
          maxLength: 255
        email:
          type: string
          format: email
        role:
          $ref: '#/components/schemas/UserRole'
        createdAt:
          type: string
          format: date-time
      required: [id, name, email, role, createdAt]

    CreateUserRequest:
      type: object
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 255
        email:
          type: string
          format: email
        role:
          $ref: '#/components/schemas/UserRole'
      required: [name, email]

    UserRole:
      type: string
      enum: [admin, member, viewer]

    UserList:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/User'
        pagination:
          $ref: '#/components/schemas/Pagination'
      required: [data, pagination]

    Pagination:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
      required: [page, limit, total]

    Error:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
      required: [code, message]
```

## Security Schemes

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          scopes:
            read:users: Read user data
            write:users: Modify user data

security:
  - BearerAuth: []
```

Per-operation security overrides the global setting:

```yaml
paths:
  /public/health:
    get:
      security: []
      responses:
        '200':
          description: Health check
```

## Tags

Group operations for documentation and code generation:

```yaml
tags:
  - name: users
    description: User management
  - name: auth
    description: Authentication and authorization
```

## operationId Best Practices

Use verb-noun format for clear code generation output. Generated TypeScript functions map directly to `operationId` values:

```yaml
paths:
  /users:
    get:
      operationId: listUsers
    post:
      operationId: createUser
  /users/{userId}:
    get:
      operationId: getUser
    put:
      operationId: updateUser
    delete:
      operationId: deleteUser
```
