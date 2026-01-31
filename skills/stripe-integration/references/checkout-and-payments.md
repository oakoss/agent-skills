---
title: Checkout and Payments
description: Checkout Sessions, Payment Intents, payment confirmation, one-time payments, and payment method configuration
tags:
  [checkout, payment-intent, one-time, client-secret, confirm, capture, search]
---

# Checkout and Payments

## Stripe Initialization

```ts
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
```

## Checkout Sessions

Checkout Sessions create a Stripe-hosted payment page. Use `mode` to specify the payment type.

### One-Time Payment

```ts
const session = await stripe.checkout.sessions.create({
  line_items: [
    {
      price: 'price_123',
      quantity: 1,
    },
    {
      price_data: {
        currency: 'usd',
        unit_amount: 2000,
        product_data: {
          name: 'T-shirt',
          description: 'Comfortable cotton t-shirt',
          images: ['https://example.com/tshirt.png'],
        },
      },
      quantity: 2,
    },
  ],
  mode: 'payment',
  success_url: 'https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
  cancel_url: 'https://example.com/cancel',
  customer_email: 'customer@example.com',
  allow_promotion_codes: true,
  billing_address_collection: 'required',
  phone_number_collection: { enabled: true },
  metadata: {
    order_id: 'order_12345',
  },
});

// Redirect customer to session.url
```

### Subscription Checkout

```ts
const session = await stripe.checkout.sessions.create({
  line_items: [{ price: 'price_monthly', quantity: 1 }],
  mode: 'subscription',
  success_url: 'https://example.com/success',
  cancel_url: 'https://example.com/cancel',
  customer: 'cus_123',
  subscription_data: {
    trial_period_days: 14,
    metadata: { plan: 'premium' },
  },
});
```

### Setup Mode (Save Payment Method)

```ts
const session = await stripe.checkout.sessions.create({
  mode: 'setup',
  customer: 'cus_123',
  success_url: 'https://example.com/success',
  cancel_url: 'https://example.com/cancel',
});
```

### Retrieve Session with Expanded Objects

```ts
const session = await stripe.checkout.sessions.retrieve('cs_123', {
  expand: ['line_items', 'customer', 'payment_intent'],
});
```

## Payment Intents

Payment Intents track the lifecycle of a payment from creation to confirmation. Use for custom payment flows (not Checkout).

### Create Payment Intent

```ts
const paymentIntent = await stripe.paymentIntents.create({
  amount: 2000,
  currency: 'usd',
  customer: 'cus_123',
  automatic_payment_methods: { enabled: true },
  description: 'Software subscription',
  metadata: {
    order_id: 'order_12345',
    product: 'pro_subscription',
  },
  receipt_email: 'customer@example.com',
  statement_descriptor: 'MYCOMPANY SUB',
});

// Send paymentIntent.client_secret to the client
```

### Confirm Payment Intent (Server-Side)

```ts
const confirmed = await stripe.paymentIntents.confirm('pi_123', {
  payment_method: 'pm_card_visa',
  return_url: 'https://example.com/order/complete',
});
```

### Manual Capture (Auth and Capture)

Useful for holding funds before fulfillment:

```ts
const paymentIntent = await stripe.paymentIntents.create({
  amount: 5000,
  currency: 'usd',
  capture_method: 'manual',
  automatic_payment_methods: { enabled: true },
});

// Later, capture the full or partial amount
const captured = await stripe.paymentIntents.capture('pi_123', {
  amount_to_capture: 4500,
});
```

### Cancel Payment Intent

```ts
const cancelled = await stripe.paymentIntents.cancel('pi_123', {
  cancellation_reason: 'requested_by_customer',
});
```

### Search Payment Intents

```ts
const results = await stripe.paymentIntents.search({
  query: "status:'succeeded' AND metadata['order_id']:'12345'",
});
```

## Payment Intent Status Flow

```text
requires_payment_method → requires_confirmation → requires_action → processing → succeeded
                                                                                → canceled
                                                                  → requires_capture (manual)
```

Key statuses:

- `requires_payment_method` -- initial state, waiting for payment details
- `requires_confirmation` -- payment method attached, ready to confirm
- `requires_action` -- 3D Secure or additional authentication needed
- `processing` -- payment is being processed
- `succeeded` -- payment completed
- `requires_capture` -- authorized but not captured (manual capture flow)

## Server Endpoint Pattern

A typical Express endpoint for creating a Payment Intent:

```ts
import express, { type Request, type Response } from 'express';

const app = express();
app.use(express.json());

app.post('/api/create-payment-intent', async (req: Request, res: Response) => {
  const { amount, currency = 'usd' } = req.body;

  const paymentIntent = await stripe.paymentIntents.create({
    amount,
    currency,
    automatic_payment_methods: { enabled: true },
  });

  res.json({ clientSecret: paymentIntent.client_secret });
});
```

## Customers

### Create Customer

```ts
const customer = await stripe.customers.create({
  email: 'user@example.com',
  name: 'Jane Doe',
  metadata: { user_id: 'usr_123' },
});
```

### Attach Payment Method to Customer

```ts
await stripe.paymentMethods.attach('pm_123', {
  customer: 'cus_123',
});

await stripe.customers.update('cus_123', {
  invoice_settings: { default_payment_method: 'pm_123' },
});
```

## Refunds

```ts
const refund = await stripe.refunds.create({
  payment_intent: 'pi_123',
  amount: 1000,
  reason: 'requested_by_customer',
});
```

Omit `amount` for a full refund.

## Idempotency

Use idempotency keys to safely retry requests:

```ts
const paymentIntent = await stripe.paymentIntents.create(
  {
    amount: 2000,
    currency: 'usd',
  },
  {
    idempotencyKey: `order_${orderId}`,
  },
);
```
