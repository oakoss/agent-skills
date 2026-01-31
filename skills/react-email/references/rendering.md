---
title: Rendering
description: Rendering emails to HTML, plain text, preview server setup, and integration with Resend, Nodemailer, and SendGrid
tags:
  [
    render,
    HTML,
    plain-text,
    preview,
    dev-server,
    Resend,
    Nodemailer,
    SendGrid,
    integration,
  ]
---

# Rendering

## The render Function

The `render` function converts React Email components into HTML strings. It is async and must be awaited.

```ts
import { render } from '@react-email/components';
```

### Basic Rendering

```ts
import { render } from '@react-email/components';
import { WelcomeEmail } from './emails/welcome';

const html = await render(<WelcomeEmail name="Sarah" />);
```

The output is a complete HTML document starting with `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"...`.

### Render Options

```ts
import { render } from '@react-email/components';
import { WelcomeEmail } from './emails/welcome';

const html = await render(<WelcomeEmail name="Sarah" />);

const prettyHtml = await render(<WelcomeEmail name="Sarah" />, {
  pretty: true,
});

const plainText = await render(<WelcomeEmail name="Sarah" />, {
  plainText: true,
});

const plainTextFormatted = await render(<WelcomeEmail name="Sarah" />, {
  plainText: true,
  htmlToTextOptions: {
    wordwrap: 80,
  },
});
```

| Option              | Type      | Description                                               |
| ------------------- | --------- | --------------------------------------------------------- |
| `pretty`            | `boolean` | Format HTML with indentation (uses Prettier internally)   |
| `plainText`         | `boolean` | Strip HTML and return plain text                          |
| `htmlToTextOptions` | `object`  | Options passed to `html-to-text` when `plainText` is true |

### Error Handling

Always wrap `render` in try/catch for production use.

```ts
import { render } from '@react-email/components';
import { OrderEmail } from './emails/order';

async function renderEmail(orderId: string) {
  try {
    const html = await render(<OrderEmail orderId={orderId} />);
    return html;
  } catch (error) {
    console.error('Failed to render email:', error);
    throw error;
  }
}
```

## Preview Server

React Email includes a local development server for previewing emails with hot reload.

### Setup

```bash
npm install react-email -D
```

Add a script to `package.json`:

```json
{
  "scripts": {
    "email:dev": "email dev"
  }
}
```

### Project Structure

The dev server looks for email templates in a specific directory.

```text
project/
├── emails/
│   ├── welcome.tsx
│   ├── order-confirmation.tsx
│   └── password-reset.tsx
├── package.json
└── ...
```

### Running the Preview

```bash
npx email dev
```

This starts a local server (default `http://localhost:3000`) that renders each email template with hot reload. Changes to email components are reflected immediately.

### Custom Source Directory

```bash
npx email dev --dir ./src/emails --port 3001
```

| Flag     | Description                                                |
| -------- | ---------------------------------------------------------- |
| `--dir`  | Directory containing email templates (default: `./emails`) |
| `--port` | Port number for the dev server (default: `3000`)           |

### Exporting Static HTML

Generate static HTML files from email templates.

```bash
npx email export --outDir ./out
```

## Integration with Email Providers

The pattern is always the same: render the React component to HTML, then pass the HTML string to your provider's send method.

### Resend

```ts
import { render } from '@react-email/components';
import { Resend } from 'resend';
import { WelcomeEmail } from './emails/welcome';

const resend = new Resend(process.env.RESEND_API_KEY);

const emailHtml = await render(<WelcomeEmail name="Alex" />);

const { data, error } = await resend.emails.send({
  from: 'onboarding@example.com',
  to: 'user@example.com',
  subject: 'Welcome to Our Platform',
  html: emailHtml,
});

if (error) {
  console.error('Resend error:', error);
}
```

Resend also supports passing the React component directly:

```ts
import { Resend } from 'resend';
import { WelcomeEmail } from './emails/welcome';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send({
  from: 'onboarding@example.com',
  to: 'user@example.com',
  subject: 'Welcome to Our Platform',
  react: WelcomeEmail({ name: 'Alex' }),
});
```

When using the `react` prop, Resend calls `render` internally. This is a Resend-specific feature and does not work with other providers.

### Nodemailer

```ts
import { render } from '@react-email/components';
import nodemailer from 'nodemailer';
import { InvoiceEmail } from './emails/invoice';

const transporter = nodemailer.createTransport({
  host: 'smtp.example.com',
  port: 465,
  secure: true,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

const emailHtml = await render(
  <InvoiceEmail invoiceId="INV-001" amount={99.99} />
);

const plainText = await render(
  <InvoiceEmail invoiceId="INV-001" amount={99.99} />,
  { plainText: true }
);

await transporter.sendMail({
  from: 'billing@example.com',
  to: 'customer@example.com',
  subject: 'Invoice #INV-001',
  html: emailHtml,
  text: plainText,
});
```

Include both `html` and `text` for maximum deliverability. Email clients that cannot render HTML will fall back to the plain text version.

### SendGrid

```ts
import { render } from '@react-email/components';
import sendgrid from '@sendgrid/mail';
import { ShippingEmail } from './emails/shipping';

sendgrid.setApiKey(process.env.SENDGRID_API_KEY || '');

const emailHtml = await render(
  <ShippingEmail orderId="12345" trackingUrl="https://example.com/track/abc" />
);

const plainText = await render(
  <ShippingEmail orderId="12345" trackingUrl="https://example.com/track/abc" />,
  { plainText: true }
);

await sendgrid.send({
  from: 'shipping@example.com',
  to: 'customer@example.com',
  subject: 'Your Order Has Shipped',
  html: emailHtml,
  text: plainText,
});
```

### AWS SES

```ts
import { render } from '@react-email/components';
import { SESClient, SendEmailCommand } from '@aws-sdk/client-ses';
import { NotificationEmail } from './emails/notification';

const ses = new SESClient({ region: 'us-east-1' });

const emailHtml = await render(<NotificationEmail message="Your report is ready" />);
const plainText = await render(
  <NotificationEmail message="Your report is ready" />,
  { plainText: true }
);

await ses.send(
  new SendEmailCommand({
    Source: 'notifications@example.com',
    Destination: {
      ToAddresses: ['user@example.com'],
    },
    Message: {
      Subject: { Data: 'New Notification' },
      Body: {
        Html: { Data: emailHtml },
        Text: { Data: plainText },
      },
    },
  })
);
```

## Email Template Pattern

Structure email templates as React components with typed props and a default export.

```tsx
import {
  Html,
  Head,
  Preview,
  Body,
  Container,
  Text,
} from '@react-email/components';

interface PasswordResetProps {
  resetUrl: string;
  expiresInHours?: number;
}

export const PasswordResetEmail = ({
  resetUrl,
  expiresInHours = 24,
}: PasswordResetProps) => {
  return (
    <Html>
      <Head />
      <Preview>Reset your password</Preview>
      <Body style={{ backgroundColor: '#f6f6f6', fontFamily: 'sans-serif' }}>
        <Container
          style={{ maxWidth: '600px', margin: '0 auto', padding: '48px 20px' }}
        >
          <Text>Click the link below to reset your password.</Text>
          <Text>This link expires in {expiresInHours} hours.</Text>
        </Container>
      </Body>
    </Html>
  );
};

PasswordResetEmail.PreviewProps = {
  resetUrl: 'https://example.com/reset?token=preview-token',
  expiresInHours: 24,
} satisfies PasswordResetProps;

export default PasswordResetEmail;
```

The `PreviewProps` static property provides default props for the preview server, making it easy to view the email during development.
