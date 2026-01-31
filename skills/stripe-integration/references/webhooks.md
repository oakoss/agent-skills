---
title: Webhooks
description: Webhook endpoints, signature verification, event handling, retry logic, and testing
tags:
  [
    webhook,
    signature,
    constructEvent,
    event,
    idempotency,
    retry,
    testing,
    express,
  ]
---

# Webhooks

## Overview

Stripe sends webhook events to notify your server about payment lifecycle changes. Webhook signature verification is critical for security -- it ensures events are genuinely from Stripe and have not been tampered with.

## Express Webhook Handler

The raw request body must be passed to `constructEvent`. Do not parse the body as JSON before verification.

```ts
import express from 'express';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

const app = express();

app.post(
  '/webhook',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const sig = req.headers['stripe-signature'];
    let event: Stripe.Event;

    try {
      event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
    } catch (err) {
      console.error(`Webhook signature verification failed: ${err.message}`);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    switch (event.type) {
      case 'payment_intent.succeeded': {
        const paymentIntent = event.data.object;
        await fulfillOrder(paymentIntent);
        break;
      }

      case 'payment_intent.payment_failed': {
        const paymentIntent = event.data.object;
        await handleFailedPayment(paymentIntent);
        break;
      }

      case 'customer.subscription.created': {
        const subscription = event.data.object;
        await provisionSubscription(subscription);
        break;
      }

      case 'customer.subscription.updated': {
        const subscription = event.data.object;
        await updateSubscriptionStatus(subscription);
        break;
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object;
        await revokeAccess(subscription);
        break;
      }

      case 'invoice.payment_succeeded': {
        const invoice = event.data.object;
        await recordPayment(invoice);
        break;
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object;
        await notifyPaymentFailure(invoice);
        break;
      }

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    res.json({ received: true });
  },
);
```

## Signature Verification Details

`constructEvent` accepts an optional tolerance parameter (in seconds) for clock skew:

```ts
const event = stripe.webhooks.constructEvent(
  rawBody,
  signatureHeader,
  webhookSecret,
  300,
);
```

The default tolerance is 300 seconds (5 minutes). Events older than the tolerance are rejected.

## Framework-Specific Raw Body

Different frameworks handle raw bodies differently. The key requirement is passing the exact bytes Stripe sent.

### Next.js App Router

```ts
import { headers } from 'next/headers';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export async function POST(request: Request) {
  const body = await request.text();
  const headersList = await headers();
  const sig = headersList.get('stripe-signature');

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET,
    );
  } catch (err) {
    return new Response(`Webhook Error: ${err.message}`, { status: 400 });
  }

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object;
      await fulfillOrder(session);
      break;
    }
  }

  return new Response(JSON.stringify({ received: true }), { status: 200 });
}
```

### Next.js Pages Router

Disable body parsing for the webhook route:

```ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { buffer } from 'micro';
import Stripe from 'stripe';

export const config = {
  api: { bodyParser: false },
};

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const buf = await buffer(req);
  const sig = req.headers['stripe-signature'];

  const event = stripe.webhooks.constructEvent(
    buf,
    sig,
    process.env.STRIPE_WEBHOOK_SECRET,
  );

  // Handle event...
  res.json({ received: true });
}
```

## Idempotent Event Handling

Stripe may deliver the same event multiple times. Use the event ID to deduplicate:

```ts
const processedEvents = new Set<string>();

async function handleWebhookEvent(event: Stripe.Event) {
  if (processedEvents.has(event.id)) {
    return;
  }

  // For production, use a database instead of in-memory Set
  await db.processedEvents.upsert({
    where: { eventId: event.id },
    create: { eventId: event.id, processedAt: new Date() },
    update: {},
  });

  // Process the event...
}
```

## Stripe Retry Schedule

If your endpoint returns a non-2xx status code, Stripe retries with exponential backoff:

| Attempt   | Delay        |
| --------- | ------------ |
| 1st retry | ~1 hour      |
| 2nd retry | ~2 hours     |
| 3rd retry | ~4 hours     |
| Continues | Up to 3 days |

After all retries are exhausted, the event is marked as failed in the Dashboard.

## Key Events by Integration

### Checkout Sessions

| Event                                      | When                                    |
| ------------------------------------------ | --------------------------------------- |
| `checkout.session.completed`               | Customer completed checkout             |
| `checkout.session.async_payment_succeeded` | Async payment (bank transfer) succeeded |
| `checkout.session.async_payment_failed`    | Async payment failed                    |
| `checkout.session.expired`                 | Session expired (24 hours)              |

### Payment Intents

| Event                            | When                               |
| -------------------------------- | ---------------------------------- |
| `payment_intent.succeeded`       | Payment completed                  |
| `payment_intent.payment_failed`  | Payment failed                     |
| `payment_intent.requires_action` | 3D Secure or authentication needed |
| `payment_intent.canceled`        | Payment canceled                   |

### Subscriptions

| Event                                  | When                        |
| -------------------------------------- | --------------------------- |
| `customer.subscription.created`        | New subscription            |
| `customer.subscription.updated`        | Plan or status change       |
| `customer.subscription.deleted`        | Subscription cancelled      |
| `customer.subscription.trial_will_end` | Trial ending in 3 days      |
| `invoice.payment_succeeded`            | Recurring payment succeeded |
| `invoice.payment_failed`               | Recurring payment failed    |

## Local Development with Stripe CLI

Forward webhook events to your local server:

```bash
stripe listen --forward-to localhost:3000/webhook
```

The CLI outputs a webhook signing secret (`whsec_...`). Use this as your `STRIPE_WEBHOOK_SECRET` during development.

Forward specific events only:

```bash
stripe listen --forward-to localhost:3000/webhook --events payment_intent.succeeded,customer.subscription.created
```

Trigger a test event:

```bash
stripe trigger payment_intent.succeeded
```

## Test Webhook Signatures

Generate test webhook signatures for unit tests without connecting to Stripe:

```ts
import Stripe from 'stripe';

const stripe = new Stripe('sk_test_fake');

const payload = JSON.stringify({
  id: 'evt_test_webhook',
  object: 'event',
  type: 'payment_intent.succeeded',
  data: {
    object: {
      id: 'pi_test',
      amount: 2000,
      currency: 'usd',
      status: 'succeeded',
    },
  },
});

const secret = 'whsec_test_secret';

const header = stripe.webhooks.generateTestHeaderString({
  payload,
  secret,
});

const event = stripe.webhooks.constructEvent(payload, header, secret);
```

## Environment Variables

```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

Store these securely. Never commit secret keys to version control. Use different keys for test and live modes.
