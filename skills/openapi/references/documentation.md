---
title: Documentation
description: Swagger UI, Redoc, API documentation best practices, and interactive documentation setup
tags: [swagger-ui, redoc, docs, documentation, api-docs, interactive]
---

# Documentation

## Swagger UI

Interactive API documentation that lets consumers explore and test endpoints directly in the browser.

### Docker Setup

```bash
docker run -p 8080:8080 -e SWAGGER_JSON=/app/openapi.yaml -v ./openapi.yaml:/app/openapi.yaml swaggerapi/swagger-ui
```

### Express Integration

```ts
import express from 'express';
import swaggerUi from 'swagger-ui-express';
import spec from './openapi.json';

const app = express();

app.use(
  '/api-docs',
  swaggerUi.serve,
  swaggerUi.setup(spec, {
    customCss: '.swagger-ui .topbar { display: none }',
    customSiteTitle: 'My API Documentation',
  }),
);
```

### HTML Standalone

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>API Docs</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"
    />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
    <script>
      SwaggerUIBundle({
        url: '/openapi.yaml',
        dom_id: '#swagger-ui',
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIBundle.SwaggerUIStandalonePreset,
        ],
        layout: 'StandaloneLayout',
      });
    </script>
  </body>
</html>
```

## Redoc

Clean, three-panel documentation with excellent navigation and search.

### HTML Standalone

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>API Reference</title>
  </head>
  <body>
    <redoc spec-url="/openapi.yaml"></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
  </body>
</html>
```

### Redoc Configuration

```html
<redoc
  spec-url="/openapi.yaml"
  hide-download-button
  required-props-first
  sort-props-alphabetically
  expand-responses="200,201"
  path-in-middle-panel
  hide-hostname
  native-scrollbars
></redoc>
```

### CLI Build

Generate a zero-dependency static HTML file:

```bash
npx @redocly/cli build-docs openapi.yaml -o docs/index.html
```

## Redocly CLI

Linting, bundling, and previewing OpenAPI specs:

```bash
npx @redocly/cli lint openapi.yaml
npx @redocly/cli bundle openapi.yaml -o dist/openapi.yaml
npx @redocly/cli preview-docs openapi.yaml
```

### Redocly Configuration

Create a `redocly.yaml` for project-wide rules:

```yaml
extends:
  - recommended

rules:
  operation-operationId: error
  operation-summary: warn
  no-path-trailing-slash: error
  no-ambiguous-paths: error
  tag-description: warn
  info-contact: warn
  no-unused-components: warn
```

## Documentation Best Practices

### Descriptions

Write concise, actionable descriptions on every element:

```yaml
paths:
  /users:
    get:
      summary: List users
      description: >
        Returns a paginated list of users. Results are sorted by creation date
        (newest first). Use query parameters to filter by role or status.
      parameters:
        - name: role
          in: query
          description: Filter users by their assigned role
          schema:
            $ref: '#/components/schemas/UserRole'
```

### Examples

Provide realistic examples at multiple levels:

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
          example: 550e8400-e29b-41d4-a716-446655440000
        name:
          type: string
          example: Jane Doe
        email:
          type: string
          format: email
          example: jane@example.com
      required: [id, name, email]

paths:
  /users/{userId}:
    get:
      responses:
        '200':
          description: User details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
              examples:
                admin:
                  summary: Admin user
                  value:
                    id: 550e8400-e29b-41d4-a716-446655440000
                    name: Jane Doe
                    email: jane@example.com
                    role: admin
                member:
                  summary: Regular member
                  value:
                    id: 7c9e6679-7425-40de-944b-e07fc1f90ae7
                    name: John Smith
                    email: john@example.com
                    role: member
```

### Tags and Grouping

Organize operations into logical groups:

```yaml
tags:
  - name: Authentication
    description: Login, logout, and token management
  - name: Users
    description: User CRUD operations and profile management
  - name: Organizations
    description: Organization management and membership

paths:
  /auth/login:
    post:
      tags: [Authentication]
      operationId: login
  /users:
    get:
      tags: [Users]
      operationId: listUsers
  /organizations:
    get:
      tags: [Organizations]
      operationId: listOrganizations
```

### Error Documentation

Document error responses consistently across all operations:

```yaml
components:
  responses:
    BadRequest:
      description: Invalid request parameters
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: BAD_REQUEST
            message: Invalid request body

    Unauthorized:
      description: Missing or invalid authentication
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: UNAUTHORIZED
            message: Authentication required

    Forbidden:
      description: Insufficient permissions
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: FORBIDDEN
            message: You do not have permission to access this resource

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: NOT_FOUND
            message: User not found

    RateLimited:
      description: Too many requests
      headers:
        Retry-After:
          schema:
            type: integer
          description: Seconds to wait before retrying
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: RATE_LIMITED
            message: Rate limit exceeded
```

### Multi-File Specs

Split large specs across files and bundle before publishing:

```text
api/
  openapi.yaml          # Root document
  paths/
    users.yaml          # /users and /users/{userId}
    auth.yaml           # /auth/*
  schemas/
    user.yaml
    error.yaml
  parameters/
    pagination.yaml
```

Reference external files:

```yaml
paths:
  /users:
    $ref: 'paths/users.yaml#/users'

components:
  schemas:
    User:
      $ref: 'schemas/user.yaml#/User'
```

Bundle into a single file for distribution:

```bash
npx @redocly/cli bundle openapi.yaml -o dist/openapi.yaml
```

### Webhooks (3.1)

OpenAPI 3.1 added top-level `webhooks` for documenting callback events:

```yaml
webhooks:
  userCreated:
    post:
      summary: User created event
      operationId: onUserCreated
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                event:
                  type: string
                  const: user.created
                data:
                  $ref: '#/components/schemas/User'
                timestamp:
                  type: string
                  format: date-time
              required: [event, data, timestamp]
      responses:
        '200':
          description: Webhook received
```
