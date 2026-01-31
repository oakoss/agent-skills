---
title: Webhooks
description: Webhook event types, signature verification with Svix, event handling patterns, and delivery monitoring with Resend
tags:
  [
    webhooks,
    events,
    svix,
    signature,
    verification,
    bounced,
    delivered,
    opened,
    clicked,
    complained,
  ]
---

# Webhooks

## Overview

Resend uses webhooks to notify your application about email lifecycle events in real time. Webhooks are powered by Svix and include cryptographic signatures for verification. Subscribe to events via the Resend dashboard or API.

## Event Types

| Event                    | Description                                                     |
| ------------------------ | --------------------------------------------------------------- |
| `email.sent`             | API request succeeded, delivery attempt in progress             |
| `email.delivered`        | Email successfully delivered to recipient's mail server         |
| `email.delivery_delayed` | Temporary delivery issue (full inbox, transient error)          |
| `email.bounced`          | Recipient's mail server permanently rejected the email          |
| `email.complained`       | Recipient marked the email as spam                              |
| `email.opened`           | Recipient opened the email (requires open tracking)             |
| `email.clicked`          | Recipient clicked a link in the email (requires click tracking) |
| `domain.created`         | New domain added to the account                                 |
| `domain.updated`         | Domain settings changed                                         |
| `domain.deleted`         | Domain removed from the account                                 |
| `contact.created`        | New contact added to an audience                                |
| `contact.updated`        | Contact information changed                                     |
| `contact.deleted`        | Contact removed from an audience                                |

## Webhook Payload Structure

All webhook payloads follow the same structure:

```json
{
  "type": "email.delivered",
  "created_at": "2024-02-22T23:41:12.126Z",
  "data": {
    "email_id": "56761188-7520-42d8-8898-ff6fc54ce618",
    "from": "Acme <onboarding@send.acme.com>",
    "to": ["user@example.com"],
    "subject": "Welcome to Acme",
    "created_at": "2024-02-22T23:41:11.894719+00:00"
  }
}
```

### Bounce Payload (Additional Fields)

```json
{
  "type": "email.bounced",
  "created_at": "2024-11-22T23:41:12.126Z",
  "data": {
    "email_id": "56761188-7520-42d8-8898-ff6fc54ce618",
    "from": "Acme <onboarding@send.acme.com>",
    "to": ["user@example.com"],
    "subject": "Welcome",
    "bounce": {
      "message": "The recipient's email address does not exist.",
      "type": "Permanent",
      "subType": "Suppressed"
    }
  }
}
```

## Signature Verification Headers

Every webhook request includes three Svix headers for verification:

| Header           | Description                            |
| ---------------- | -------------------------------------- |
| `svix-id`        | Unique message identifier              |
| `svix-timestamp` | Unix timestamp of the webhook dispatch |
| `svix-signature` | HMAC signature for payload validation  |

## Verify with Resend SDK

The Resend SDK provides a built-in method for webhook verification.

```ts
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

const payload = await resend.webhooks.verify({
  payload: JSON.stringify(req.body),
  headers: {
    id: req.headers['svix-id'] as string,
    timestamp: req.headers['svix-timestamp'] as string,
    signature: req.headers['svix-signature'] as string,
  },
  webhookSecret: process.env.RESEND_WEBHOOK_SECRET!,
});
```

## Verify with Svix Library

For manual verification without the Resend SDK.

```ts
import { Webhook } from 'svix';

const wh = new Webhook(process.env.RESEND_WEBHOOK_SECRET!);

const payload = wh.verify(rawBody, {
  'svix-id': req.headers['svix-id'] as string,
  'svix-timestamp': req.headers['svix-timestamp'] as string,
  'svix-signature': req.headers['svix-signature'] as string,
});
```

## Next.js Route Handler Example

```ts
import { Resend } from 'resend';
import { NextRequest, NextResponse } from 'next/server';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(req: NextRequest) {
  const body = await req.text();

  let payload;
  try {
    payload = await resend.webhooks.verify({
      payload: body,
      headers: {
        id: req.headers.get('svix-id')!,
        timestamp: req.headers.get('svix-timestamp')!,
        signature: req.headers.get('svix-signature')!,
      },
      webhookSecret: process.env.RESEND_WEBHOOK_SECRET!,
    });
  } catch {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 401 });
  }

  switch (payload.type) {
    case 'email.delivered':
      await handleDelivered(payload.data);
      break;
    case 'email.bounced':
      await handleBounced(payload.data);
      break;
    case 'email.complained':
      await handleComplained(payload.data);
      break;
    case 'email.opened':
      await handleOpened(payload.data);
      break;
    case 'email.clicked':
      await handleClicked(payload.data);
      break;
  }

  return NextResponse.json({ received: true });
}
```

## Express Route Handler Example

```ts
import express from 'express';
import { Webhook } from 'svix';

const app = express();
app.use(express.raw({ type: 'application/json' }));

app.post('/api/webhooks/resend', (req, res) => {
  const wh = new Webhook(process.env.RESEND_WEBHOOK_SECRET!);

  let payload;
  try {
    payload = wh.verify(req.body.toString(), {
      'svix-id': req.headers['svix-id'] as string,
      'svix-timestamp': req.headers['svix-timestamp'] as string,
      'svix-signature': req.headers['svix-signature'] as string,
    });
  } catch {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  const { type, data } = payload as {
    type: string;
    data: Record<string, unknown>;
  };

  switch (type) {
    case 'email.delivered':
      console.log('Delivered:', data.email_id);
      break;
    case 'email.bounced':
      console.log('Bounced:', data.email_id, data.bounce);
      break;
    case 'email.complained':
      console.log('Complaint:', data.email_id);
      break;
  }

  res.json({ received: true });
});
```

## TypeScript Event Types

```ts
interface ResendWebhookEvent {
  type: string;
  created_at: string;
  data: EmailEventData;
}

interface EmailEventData {
  email_id: string;
  from: string;
  to: string[];
  subject: string;
  created_at: string;
  broadcast_id?: string;
  template_id?: string;
  tags?: Record<string, string>;
  bounce?: {
    message: string;
    type: 'Permanent' | 'Transient';
    subType: string;
  };
}
```

## Monitoring Best Practices

### Handle Bounces

Remove or suppress addresses that permanently bounce to protect sender reputation.

```ts
async function handleBounced(data: EmailEventData) {
  if (data.bounce?.type === 'Permanent') {
    await db.user.update({
      where: { email: data.to[0] },
      data: { emailStatus: 'bounced', emailSuppressed: true },
    });
  }
}
```

### Handle Complaints

Immediately unsubscribe users who mark emails as spam.

```ts
async function handleComplained(data: EmailEventData) {
  await db.user.update({
    where: { email: data.to[0] },
    data: { emailOptOut: true },
  });
}
```

### Track Engagement

Use open and click events to measure email effectiveness.

```ts
async function handleOpened(data: EmailEventData) {
  await db.emailEvent.create({
    data: {
      emailId: data.email_id,
      type: 'opened',
      recipientEmail: data.to[0],
      timestamp: new Date(),
    },
  });
}
```

## Webhook Security Checklist

- Always verify the Svix signature before processing events
- Use the raw request body for verification (not parsed JSON)
- Store the webhook secret in an environment variable (`RESEND_WEBHOOK_SECRET`)
- Return a `2xx` status code promptly to avoid retries
- Process events asynchronously after acknowledging receipt
- Implement idempotent event handlers (webhooks may be retried)
- Log unrecognized event types instead of failing
