---
title: Sending Emails
description: Send emails with Resend including single send, batch sending, React Email, attachments, scheduling, idempotency, tags, and templates
tags:
  [
    send,
    batch,
    attachments,
    scheduling,
    idempotency,
    react-email,
    tags,
    templates,
  ]
---

# Sending Emails

## Basic Email Send

```ts
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send({
  from: 'Acme <notifications@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Welcome to Acme',
  html: '<h1>Welcome!</h1><p>Thanks for signing up.</p>',
});

if (error) {
  console.error('Failed to send email:', error);
  return;
}

console.log('Email sent:', data.id);
```

## Send with Plain Text

```ts
const { data, error } = await resend.emails.send({
  from: 'Acme <notifications@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Your receipt',
  text: 'Thank you for your purchase. Order #12345.',
});
```

## Send with React Email (Node.js SDK Only)

```tsx
import { Resend } from 'resend';
import { WelcomeEmail } from './emails/welcome';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send({
  from: 'Acme <welcome@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Welcome to Acme',
  react: <WelcomeEmail username="Jane" />,
});
```

## React Email Component Example

```tsx
import {
  Html,
  Head,
  Body,
  Container,
  Text,
  Button,
} from '@react-email/components';

interface WelcomeEmailProps {
  username: string;
}

export function WelcomeEmail({ username }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Body style={{ fontFamily: 'sans-serif' }}>
        <Container>
          <Text>Hello {username},</Text>
          <Text>Welcome to Acme! Get started by verifying your account.</Text>
          <Button
            href="https://acme.com/verify"
            style={{ background: '#000', color: '#fff', padding: '12px 20px' }}
          >
            Verify Account
          </Button>
        </Container>
      </Body>
    </Html>
  );
}
```

## Multiple Recipients, CC, and BCC

```ts
const { data, error } = await resend.emails.send({
  from: 'Acme <notifications@send.acme.com>',
  to: ['alice@example.com', 'bob@example.com'],
  cc: ['manager@example.com'],
  bcc: ['audit@acme.com'],
  reply_to: 'support@acme.com',
  subject: 'Team Update',
  html: '<p>Here is the weekly update.</p>',
});
```

## Attachments

Attachments can be provided as base64 content or a URL path. Max 40MB total per email after encoding.

```ts
const { data, error } = await resend.emails.send({
  from: 'Acme <billing@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Your Invoice',
  html: '<p>Please find your invoice attached.</p>',
  attachments: [
    {
      filename: 'invoice.pdf',
      content: invoicePdfBuffer,
    },
  ],
});
```

### Attachment via URL

```ts
const { data, error } = await resend.emails.send({
  from: 'Acme <reports@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Monthly Report',
  html: '<p>Your monthly report is attached.</p>',
  attachments: [
    {
      filename: 'report.pdf',
      path: 'https://acme.com/reports/2024-01.pdf',
    },
  ],
});
```

### Inline Image Attachment

```ts
const { data, error } = await resend.emails.send({
  from: 'Acme <news@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Newsletter',
  html: '<p>Check this out:</p><img src="cid:logo" />',
  attachments: [
    {
      filename: 'logo.png',
      content: logoPngBuffer,
      content_type: 'image/png',
      content_id: 'logo',
    },
  ],
});
```

## Scheduled Sending

Schedule emails for future delivery using ISO 8601 format or natural language.

```ts
const { data, error } = await resend.emails.send({
  from: 'Acme <reminders@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Reminder: Your trial expires tomorrow',
  html: '<p>Your free trial expires in 24 hours.</p>',
  scheduled_at: '2024-12-25T09:00:00.000Z',
});
```

### Natural Language Scheduling

```ts
const { data, error } = await resend.emails.send({
  from: 'Acme <reminders@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Follow-up',
  html: '<p>Just checking in.</p>',
  scheduled_at: 'in 1 hour',
});
```

## Idempotent Sends

Prevent duplicate emails when retrying failed requests by providing an idempotency key.

```ts
const { data, error } = await resend.emails.send(
  {
    from: 'Acme <orders@send.acme.com>',
    to: ['user@example.com'],
    subject: 'Order Confirmation #12345',
    html: '<p>Your order has been confirmed.</p>',
  },
  {
    idempotencyKey: 'order-confirm/12345',
  },
);
```

### Batch Send with Idempotency

```ts
const { data, error } = await resend.batch.send(
  [
    {
      from: 'Acme <notifications@send.acme.com>',
      to: ['alice@example.com'],
      subject: 'Weekly Digest',
      html: '<p>Your weekly digest.</p>',
    },
    {
      from: 'Acme <notifications@send.acme.com>',
      to: ['bob@example.com'],
      subject: 'Weekly Digest',
      html: '<p>Your weekly digest.</p>',
    },
  ],
  {
    idempotencyKey: 'weekly-digest/2024-w03',
  },
);
```

## Batch Sending

Send multiple emails in a single API request. Attachments and scheduling are not supported in batch requests.

```ts
const { data, error } = await resend.batch.send([
  {
    from: 'Acme <onboarding@send.acme.com>',
    to: ['user1@example.com'],
    subject: 'Welcome!',
    html: '<h1>Welcome to Acme!</h1>',
  },
  {
    from: 'Acme <onboarding@send.acme.com>',
    to: ['user2@example.com'],
    subject: 'Welcome!',
    html: '<h1>Welcome to Acme!</h1>',
  },
]);

if (error) {
  console.error('Batch send failed:', error);
  return;
}

console.log('Sent emails:', data);
```

## Tags for Categorization

Tags are key-value pairs for categorizing and filtering emails. Names and values must use ASCII letters, numbers, underscores, or dashes (max 256 chars each).

```ts
const { data, error } = await resend.emails.send({
  from: 'Acme <notifications@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Password Reset',
  html: '<p>Click the link to reset your password.</p>',
  tags: [
    { name: 'category', value: 'password_reset' },
    { name: 'user_id', value: '12345' },
  ],
});
```

## Custom Headers

```ts
const { data, error } = await resend.emails.send({
  from: 'Acme <notifications@send.acme.com>',
  to: ['user@example.com'],
  subject: 'Update',
  html: '<p>Important update.</p>',
  headers: {
    'X-Entity-Ref-ID': 'unique-ref-123',
    'List-Unsubscribe': '<https://acme.com/unsubscribe>',
  },
});
```

## Retrieve Email Status

```ts
const { data, error } = await resend.emails.get('email_id_12345');

if (data) {
  console.log('Status:', data.last_event);
}
```

## Error Handling Pattern

```ts
async function sendEmail(to: string, subject: string, html: string) {
  const { data, error } = await resend.emails.send({
    from: 'Acme <notifications@send.acme.com>',
    to: [to],
    subject,
    html,
  });

  if (error) {
    if (error.name === 'validation_error') {
      throw new Error(`Invalid email params: ${error.message}`);
    }
    if (error.name === 'rate_limit_exceeded') {
      throw new Error('Rate limited, retry later');
    }
    throw new Error(`Email send failed: ${error.message}`);
  }

  return data.id;
}
```

## REST API (cURL)

```bash
curl -X POST 'https://api.resend.com/emails' \
  -H 'Authorization: Bearer re_xxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "Acme <notifications@send.acme.com>",
    "to": ["user@example.com"],
    "subject": "Hello",
    "html": "<p>Hello world</p>"
  }'
```

### With Idempotency Key (cURL)

```bash
curl -X POST 'https://api.resend.com/emails' \
  -H 'Authorization: Bearer re_xxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: order-confirm/12345' \
  -d '{
    "from": "Acme <notifications@send.acme.com>",
    "to": ["user@example.com"],
    "subject": "Order Confirmation",
    "html": "<p>Your order is confirmed.</p>"
  }'
```
