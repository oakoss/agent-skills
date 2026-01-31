---
title: Stripe Elements
description: React Stripe.js setup, Elements provider, PaymentElement, custom payment forms, and appearance customization
tags:
  [
    elements,
    react,
    payment-element,
    loadStripe,
    useStripe,
    useElements,
    appearance,
    form,
  ]
---

# Stripe Elements

## Installation

```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

## Load Stripe

Call `loadStripe` once at module level, not inside a component:

```ts
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY,
);
```

## Elements Provider

The `Elements` provider gives child components access to Stripe.js. There are two initialization modes.

### Deferred Intent Mode (Recommended for Flexibility)

Create the PaymentIntent after the customer fills in payment details:

```tsx
import { Elements } from '@stripe/react-stripe-js';

function App() {
  const options = {
    mode: 'payment' as const,
    amount: 1099,
    currency: 'usd',
    appearance: {
      theme: 'stripe' as const,
    },
  };

  return (
    <Elements stripe={stripePromise} options={options}>
      <CheckoutForm />
    </Elements>
  );
}
```

### Client Secret Mode

Pass a `clientSecret` from an existing PaymentIntent or SetupIntent:

```tsx
import { Elements } from '@stripe/react-stripe-js';

function App({ clientSecret }: { clientSecret: string }) {
  const options = {
    clientSecret,
    appearance: {
      theme: 'stripe' as const,
    },
  };

  return (
    <Elements stripe={stripePromise} options={options}>
      <CheckoutForm />
    </Elements>
  );
}
```

## Payment Form with PaymentElement

`PaymentElement` renders a dynamic form that supports cards, wallets, bank transfers, and other payment methods based on your Stripe Dashboard configuration.

### Deferred Intent Flow

```tsx
import {
  useStripe,
  useElements,
  PaymentElement,
} from '@stripe/react-stripe-js';

function CheckoutForm() {
  const stripe = useStripe();
  const elements = useElements();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);

    const { error: submitError } = await elements.submit();
    if (submitError) {
      setErrorMessage(submitError.message ?? 'Validation failed');
      setProcessing(false);
      return;
    }

    const res = await fetch('/api/create-payment-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount: 1099, currency: 'usd' }),
    });

    const { clientSecret } = await res.json();

    const { error } = await stripe.confirmPayment({
      elements,
      clientSecret,
      confirmParams: {
        return_url: `${window.location.origin}/order/complete`,
      },
    });

    if (error) {
      setErrorMessage(error.message ?? 'Payment failed');
    }

    setProcessing(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <button disabled={!stripe || processing} type="submit">
        {processing ? 'Processing...' : 'Pay $10.99'}
      </button>
      {errorMessage ? <div>{errorMessage}</div> : null}
    </form>
  );
}
```

### Client Secret Flow

```tsx
function CheckoutForm() {
  const stripe = useStripe();
  const elements = useElements();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);

    const { error, paymentIntent } = await stripe.confirmPayment({
      elements,
      redirect: 'if_required',
      confirmParams: {
        return_url: `${window.location.origin}/order/complete`,
      },
    });

    if (error) {
      setErrorMessage(error.message ?? 'Payment failed');
    } else if (paymentIntent?.status === 'succeeded') {
      setErrorMessage(null);
    }

    setProcessing(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <button disabled={!stripe || processing} type="submit">
        {processing ? 'Processing...' : 'Pay'}
      </button>
      {errorMessage ? <div>{errorMessage}</div> : null}
    </form>
  );
}
```

## PaymentElement Options

```tsx
<PaymentElement
  options={{
    layout: {
      type: 'tabs',
      defaultCollapsed: false,
    },
    fields: {
      billingDetails: {
        address: {
          country: 'auto',
        },
      },
    },
    wallets: {
      applePay: 'auto',
      googlePay: 'auto',
    },
  }}
/>
```

Layout options:

- `tabs` -- payment methods shown as tabs (default)
- `accordion` -- payment methods shown as collapsible sections

## LinkAuthenticationElement

Enables Stripe Link for faster checkout with saved payment details:

```tsx
import {
  LinkAuthenticationElement,
  PaymentElement,
} from '@stripe/react-stripe-js';

function CheckoutForm() {
  const [email, setEmail] = useState('');

  return (
    <form onSubmit={handleSubmit}>
      <LinkAuthenticationElement
        options={{ defaultValues: { email: '' } }}
        onChange={(event) => {
          if (event.complete) {
            setEmail(event.value.email);
          }
        }}
      />
      <PaymentElement options={{ layout: 'tabs' }} />
      <button type="submit">Pay</button>
    </form>
  );
}
```

## AddressElement

Collect shipping or billing addresses:

```tsx
import { AddressElement } from '@stripe/react-stripe-js';

function ShippingForm() {
  return (
    <AddressElement
      options={{
        mode: 'shipping',
        allowedCountries: ['US', 'CA', 'GB'],
        autocomplete: { mode: 'google_maps_api', apiKey: 'YOUR_KEY' },
      }}
      onChange={(event) => {
        if (event.complete) {
          const address = event.value;
        }
      }}
    />
  );
}
```

## Appearance API

Customize the look of all Elements to match your brand:

```ts
const appearance: Stripe.Appearance = {
  theme: 'stripe',
  variables: {
    colorPrimary: '#0570de',
    colorBackground: '#ffffff',
    colorText: '#30313d',
    colorDanger: '#df1b41',
    fontFamily: 'system-ui, sans-serif',
    spacingUnit: '4px',
    borderRadius: '4px',
  },
  rules: {
    '.Input': {
      border: '1px solid #e0e0e0',
      boxShadow: 'none',
    },
    '.Input:focus': {
      border: '1px solid #0570de',
      boxShadow: '0 0 0 1px #0570de',
    },
    '.Label': {
      fontWeight: '500',
    },
  },
};
```

Available themes: `stripe`, `night`, `flat`.

## Setup Mode (Save Card for Later)

```tsx
function App({ clientSecret }: { clientSecret: string }) {
  return (
    <Elements
      stripe={stripePromise}
      options={{ clientSecret, appearance: { theme: 'stripe' } }}
    >
      <SetupForm />
    </Elements>
  );
}

function SetupForm() {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    const { error } = await stripe.confirmSetup({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/account`,
      },
    });

    if (error) {
      console.error(error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <button type="submit">Save Payment Method</button>
    </form>
  );
}
```

## Server-Side: Create PaymentIntent Endpoint

```ts
import Stripe from 'stripe';
import express from 'express';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
const app = express();

app.use(express.json());

app.post('/api/create-payment-intent', async (req, res) => {
  const { amount, currency = 'usd' } = req.body;

  const paymentIntent = await stripe.paymentIntents.create({
    amount,
    currency,
    automatic_payment_methods: { enabled: true },
  });

  res.json({ clientSecret: paymentIntent.client_secret });
});
```
