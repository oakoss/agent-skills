---
title: Contacts and Broadcasts
description: Contacts management, Segments (formerly Audiences), Broadcasts for bulk sending, unsubscribe handling, and template variables
tags:
  [
    contacts,
    segments,
    audiences,
    broadcasts,
    bulk-email,
    unsubscribe,
    template-variables,
  ]
---

# Contacts and Broadcasts

Resend provides Contacts, Segments, and Broadcasts for managing recipients and sending bulk emails. Contacts are global entities linked to an email address. Segments group contacts for targeted sending. Broadcasts deliver emails to entire segments.

## Contacts

### Create a Contact

```ts
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.contacts.create({
  email: 'steve@example.com',
  firstName: 'Steve',
  lastName: 'Wozniak',
  unsubscribed: false,
});
```

### List Contacts

```ts
const { data, error } = await resend.contacts.list();
```

### Get a Contact

```ts
const { data, error } = await resend.contacts.get('contact-id');
```

### Update a Contact

```ts
const { data, error } = await resend.contacts.update({
  id: 'contact-id',
  firstName: 'Updated Name',
  unsubscribed: false,
});
```

### Update by Email

```ts
const { data, error } = await resend.contacts.update({
  email: 'steve@example.com',
  unsubscribed: true,
});
```

### Delete a Contact

```ts
const { data, error } = await resend.contacts.remove('contact-id');
```

### Contact with Custom Properties

Contacts support custom key-value properties for personalization in broadcasts.

```ts
const { data, error } = await resend.contacts.create({
  email: 'user@example.com',
  firstName: 'Jane',
  lastName: 'Doe',
  properties: {
    company_name: 'Acme Corp',
    plan: 'enterprise',
  },
});
```

## Broadcasts

Broadcasts send emails to an entire segment of contacts.

### Create a Broadcast

```ts
const { data, error } = await resend.broadcasts.create({
  from: 'Acme <newsletter@send.acme.com>',
  subject: 'Monthly Newsletter',
  html: 'Hi {{{FIRST_NAME|there}}}, check out our latest updates.',
});
```

### Send a Broadcast

```ts
const { data, error } = await resend.broadcasts.send('broadcast-id', {
  segmentId: 'segment-id',
  scheduledAt: '2025-01-15T09:00:00.000Z',
});
```

### Update a Broadcast

```ts
const { data, error } = await resend.broadcasts.update('broadcast-id', {
  subject: 'Updated Subject Line',
  html: 'Updated content with {{{FIRST_NAME|friend}}}.',
});
```

### List Broadcasts

```ts
const { data, error } = await resend.broadcasts.list();
```

### Get a Broadcast

```ts
const { data, error } = await resend.broadcasts.get('broadcast-id');
```

### Delete a Broadcast

```ts
const { data, error } = await resend.broadcasts.remove('broadcast-id');
```

## Template Variables

Broadcasts support personalization with triple-brace template variables. The value after `|` is the fallback when the contact property is missing.

| Variable                       | Description                           |
| ------------------------------ | ------------------------------------- |
| `{{{FIRST_NAME\|there}}}`      | Contact first name with fallback      |
| `{{{LAST_NAME\|friend}}}`      | Contact last name with fallback       |
| `{{{EMAIL}}}`                  | Contact email address                 |
| `{{{RESEND_UNSUBSCRIBE_URL}}}` | One-click unsubscribe link (required) |

### Example Broadcast HTML

```html
<h1>Hi {{{FIRST_NAME|there}}},</h1>
<p>Here is your weekly digest from Acme.</p>
<p>
  <a href="{{{RESEND_UNSUBSCRIBE_URL}}}">Unsubscribe</a>
</p>
```

Always include `{{{RESEND_UNSUBSCRIBE_URL}}}` in broadcast emails for compliance with anti-spam regulations.

## REST API Examples

### Create Contact (cURL)

```bash
curl -X POST 'https://api.resend.com/contacts' \
  -H 'Authorization: Bearer re_xxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "firstName": "Jane",
    "lastName": "Doe",
    "unsubscribed": false
  }'
```

### Create and Send Broadcast (cURL)

```bash
curl -X POST 'https://api.resend.com/broadcasts' \
  -H 'Authorization: Bearer re_xxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "segment_id": "segment-id-here",
    "from": "Acme <newsletter@send.acme.com>",
    "subject": "Weekly Update",
    "html": "Hi {{{FIRST_NAME|there}}}, here are your updates."
  }'
```

## Migration from Audiences to Segments

Resend renamed Audiences to Segments. The Contacts model is now global rather than scoped per audience. Existing audience IDs continue to work as segment IDs during the migration period.
