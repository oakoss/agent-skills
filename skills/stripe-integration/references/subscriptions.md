---
title: Subscriptions
description: Subscription lifecycle, pricing models, trials, proration, Customer Portal, and billing management
tags:
  [
    subscription,
    billing,
    trial,
    proration,
    customer-portal,
    pricing,
    metered,
    cancel,
    update,
  ]
---

# Subscriptions

## Create Subscription

Use `payment_behavior: 'default_incomplete'` to handle SCA (Strong Customer Authentication) properly. Expand `latest_invoice.payment_intent` to get the `client_secret` for client-side confirmation.

```ts
const subscription = await stripe.subscriptions.create({
  customer: 'cus_123',
  items: [{ price: 'price_monthly' }],
  payment_behavior: 'default_incomplete',
  payment_settings: {
    save_default_payment_method: 'on_subscription',
  },
  expand: ['latest_invoice.payment_intent'],
});

// Send client_secret to frontend for payment confirmation
const clientSecret = subscription.latest_invoice?.payment_intent?.client_secret;
```

## Subscription with Trial

```ts
const subscription = await stripe.subscriptions.create({
  customer: 'cus_123',
  items: [{ price: 'price_monthly' }],
  trial_period_days: 14,
  payment_settings: {
    save_default_payment_method: 'on_subscription',
  },
  trial_settings: {
    end_behavior: { missing_payment_method: 'cancel' },
  },
});
```

## Multiple Line Items

```ts
const subscription = await stripe.subscriptions.create({
  customer: 'cus_123',
  items: [
    { price: 'price_base_plan', quantity: 1 },
    { price: 'price_per_seat', quantity: 5 },
  ],
  payment_behavior: 'default_incomplete',
  expand: ['latest_invoice.payment_intent'],
});
```

## Update Subscription (Plan Change)

Always set `proration_behavior` explicitly to avoid unexpected charges.

```ts
const subscription = await stripe.subscriptions.retrieve('sub_123');

const updated = await stripe.subscriptions.update('sub_123', {
  items: [
    {
      id: subscription.items.data[0].id,
      price: 'price_new_plan',
    },
  ],
  proration_behavior: 'create_prorations',
  metadata: { upgraded_at: new Date().toISOString() },
});
```

### Proration Behavior Options

- `create_prorations` -- generate proration invoice items (default)
- `none` -- no proration, new price applies at next billing cycle
- `always_invoice` -- create prorations and immediately invoice

## Cancel Subscription

### Cancel at Period End (Recommended)

```ts
const subscription = await stripe.subscriptions.update('sub_123', {
  cancel_at_period_end: true,
});
```

### Cancel Immediately

```ts
const cancelled = await stripe.subscriptions.cancel('sub_123', {
  prorate: true,
  invoice_now: true,
});
```

### Resume Cancelled Subscription

Only works if `cancel_at_period_end` is true and the period has not ended:

```ts
const resumed = await stripe.subscriptions.update('sub_123', {
  cancel_at_period_end: false,
});
```

## Pause Subscription

```ts
const paused = await stripe.subscriptions.update('sub_123', {
  pause_collection: {
    behavior: 'mark_uncollectible',
    resumes_at: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60,
  },
});
```

## Retrieve Subscription

```ts
const subscription = await stripe.subscriptions.retrieve('sub_123', {
  expand: ['customer', 'default_payment_method', 'latest_invoice'],
});
```

## Subscription Status Flow

```text
incomplete → active → past_due → canceled
                    → unpaid → canceled
active → trialing → active
active → paused → active
```

Key statuses:

- `incomplete` -- initial payment failed or requires action
- `trialing` -- in free trial period
- `active` -- payment succeeded, subscription is active
- `past_due` -- latest invoice payment failed, retry in progress
- `unpaid` -- all retry attempts exhausted
- `canceled` -- subscription ended

## Pricing Models

### Fixed Price

Create a price with a fixed recurring amount:

```ts
const price = await stripe.prices.create({
  currency: 'usd',
  unit_amount: 1500,
  recurring: { interval: 'month' },
  product: 'prod_123',
});
```

### Per-Seat Pricing

Use quantity to represent seats:

```ts
const subscription = await stripe.subscriptions.create({
  customer: 'cus_123',
  items: [{ price: 'price_per_seat', quantity: 10 }],
});

// Update seat count
await stripe.subscriptions.update('sub_123', {
  items: [{ id: 'si_123', quantity: 15 }],
  proration_behavior: 'create_prorations',
});
```

### Metered / Usage-Based Billing

Create a metered price and report usage:

```ts
const price = await stripe.prices.create({
  currency: 'usd',
  unit_amount: 5,
  recurring: {
    interval: 'month',
    usage_type: 'metered',
  },
  product: 'prod_123',
});

// Report usage for a subscription item
await stripe.subscriptionItems.createUsageRecord('si_123', {
  quantity: 100,
  timestamp: Math.floor(Date.now() / 1000),
  action: 'increment',
});
```

## Customer Portal

The Customer Portal is a Stripe-hosted UI where customers manage subscriptions and billing. Save portal settings in the Dashboard before creating sessions.

### Create Portal Session

```ts
const portalSession = await stripe.billingPortal.sessions.create({
  customer: 'cus_123',
  return_url: 'https://example.com/account',
});

// Redirect customer to portalSession.url
```

### Portal Configuration

Create custom portal configurations for different customer segments:

```ts
const configuration = await stripe.billingPortal.configurations.create({
  business_profile: {
    headline: 'Manage your subscription',
  },
  features: {
    subscription_cancel: { enabled: true },
    subscription_update: {
      enabled: true,
      default_allowed_updates: ['price', 'quantity'],
      products: [
        {
          product: 'prod_123',
          prices: ['price_basic', 'price_pro', 'price_enterprise'],
        },
      ],
    },
    payment_method_update: { enabled: true },
    invoice_history: { enabled: true },
  },
});

// Use configuration when creating portal session
const session = await stripe.billingPortal.sessions.create({
  customer: 'cus_123',
  configuration: configuration.id,
  return_url: 'https://example.com/account',
});
```

### Express Route for Portal

```ts
app.post('/api/create-portal-session', async (req, res) => {
  const { customerId } = req.body;

  const portalSession = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${req.headers.origin}/account`,
  });

  res.json({ url: portalSession.url });
});
```

## Key Webhook Events for Subscriptions

| Event                                  | When                              |
| -------------------------------------- | --------------------------------- |
| `customer.subscription.created`        | New subscription created          |
| `customer.subscription.updated`        | Status, plan, or quantity changed |
| `customer.subscription.deleted`        | Subscription cancelled            |
| `customer.subscription.trial_will_end` | Trial ending in 3 days            |
| `invoice.payment_succeeded`            | Recurring payment succeeded       |
| `invoice.payment_failed`               | Recurring payment failed          |
| `invoice.finalized`                    | Invoice ready for payment         |
