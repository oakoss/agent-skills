---
title: Components
description: Built-in React Email components for document structure, content, and layout
tags:
  [
    Html,
    Head,
    Body,
    Container,
    Section,
    Row,
    Column,
    Text,
    Heading,
    Link,
    Button,
    Img,
    Hr,
    Preview,
    Font,
    Tailwind,
  ]
---

# Components

All components are imported from `@react-email/components`.

```tsx
import {
  Html,
  Head,
  Body,
  Container,
  Section,
  Row,
  Column,
  Text,
  Heading,
  Link,
  Button,
  Img,
  Hr,
  Preview,
  Font,
  Tailwind,
} from '@react-email/components';
```

## Document Structure

Every email starts with `Html`, `Head`, and `Body`. These map to the root HTML document structure.

```tsx
import { Html, Head, Body, Container, Text } from '@react-email/components';

export const BasicEmail = () => {
  return (
    <Html lang="en" dir="ltr">
      <Head />
      <Body style={{ backgroundColor: '#ffffff', fontFamily: 'sans-serif' }}>
        <Container style={{ maxWidth: '600px', margin: '0 auto' }}>
          <Text>Hello from React Email</Text>
        </Container>
      </Body>
    </Html>
  );
};
```

### Html

Root element. Accepts `lang` and `dir` props for internationalization.

### Head

Place inside `Html` before `Body`. Used to load `Font` components, meta tags, and the `title` element. Renders as an empty self-closing tag when no children are needed.

### Body

Wraps all visible email content. Apply global background color and font-family here.

### Container

Centers content horizontally and constrains width. Use one `Container` per email. Set `maxWidth` via style (typically `600px` for email).

## Content Components

### Text

Renders a `<p>` tag. Supports margin shorthand props (`m`, `mx`, `my`, `mt`, `mr`, `mb`, `ml`).

```tsx
import { Text } from '@react-email/components';

const Email = () => {
  return (
    <Text style={{ fontSize: '16px', lineHeight: '24px', color: '#333333' }}>
      Thank you for your purchase. Your order is being processed.
    </Text>
  );
};
```

### Heading

Renders semantic heading elements (`h1`-`h6`). Use the `as` prop to set the level.

```tsx
import { Heading } from '@react-email/components';

const Email = () => {
  return (
    <>
      <Heading as="h1" style={{ fontSize: '24px', fontWeight: '600' }}>
        Welcome
      </Heading>
      <Heading as="h2" mt="16px" mb="8px">
        Your Account
      </Heading>
    </>
  );
};
```

Heading supports margin shorthand props: `m`, `mx`, `my`, `mt`, `mr`, `mb`, `ml`.

### Link

Renders an anchor tag. Always set `href`. Use `target="_blank"` for external links.

```tsx
import { Link } from '@react-email/components';

const Email = () => {
  return (
    <Link
      href="https://example.com/dashboard"
      style={{ color: '#5469d4', textDecoration: 'underline' }}
    >
      View Dashboard
    </Link>
  );
};
```

### Button

Renders a link styled as a button. Requires `href`. Renders using a table-based structure for maximum email client compatibility.

```tsx
import { Button } from '@react-email/components';

const Email = () => {
  return (
    <Button
      href="https://example.com/verify?token=abc123"
      style={{
        backgroundColor: '#5469d4',
        color: '#ffffff',
        padding: '12px 24px',
        borderRadius: '4px',
        textDecoration: 'none',
        fontWeight: '600',
        display: 'inline-block',
      }}
    >
      Verify Email Address
    </Button>
  );
};
```

### Img

Renders an image. Always specify `width`, `height`, and `alt` to prevent layout shifts and improve accessibility.

```tsx
import { Img } from '@react-email/components';

const Email = () => {
  return (
    <Img
      src="https://example.com/logo.png"
      width="150"
      height="40"
      alt="Company Logo"
      style={{ margin: '0 auto', display: 'block' }}
    />
  );
};
```

Use absolute URLs for `src` in production. Relative paths only work in the preview server.

### Hr

Renders a horizontal rule. Style with `borderColor` and `margin`.

```tsx
import { Hr } from '@react-email/components';

const Email = () => {
  return <Hr style={{ borderColor: '#e6e6e6', margin: '32px 0' }} />;
};
```

### Preview

Sets the preview text shown in email client inbox lists (next to the subject line). Place as a direct child of `Html`, before `Body`.

```tsx
import { Html, Preview, Body, Text } from '@react-email/components';

const Email = () => {
  return (
    <Html>
      <Preview>Your order #12345 has shipped and is on its way</Preview>
      <Body>
        <Text>Order details below...</Text>
      </Body>
    </Html>
  );
};
```

Without a `Preview` component, email clients display the first visible body text as the preview.

## Layout Components

Email clients do not support CSS Grid or Flexbox reliably. React Email provides table-based layout components.

### Section

Groups related content. Renders as a `<table>` element internally.

```tsx
import { Section, Text } from '@react-email/components';

const Email = () => {
  return (
    <Section style={{ padding: '24px', backgroundColor: '#f9f9f9' }}>
      <Text>This section has a background color and padding.</Text>
    </Section>
  );
};
```

### Row and Column

Create multi-column layouts. `Row` renders as a table row, `Column` as a table cell. Always use inside a `Section`.

```tsx
import { Section, Row, Column, Img, Text } from '@react-email/components';

const Email = () => {
  return (
    <Section>
      <Row>
        <Column style={{ width: '50%', verticalAlign: 'top' }}>
          <Img
            src="https://example.com/product.png"
            width="200"
            height="200"
            alt="Product"
          />
        </Column>
        <Column
          style={{ width: '50%', verticalAlign: 'top', paddingLeft: '16px' }}
        >
          <Text style={{ fontWeight: 'bold', fontSize: '18px' }}>
            Product Name
          </Text>
          <Text style={{ color: '#666666' }}>$29.99</Text>
        </Column>
      </Row>
    </Section>
  );
};
```

### Three-Column Layout

```tsx
import { Section, Row, Column, Text } from '@react-email/components';

const Email = () => {
  return (
    <Section>
      <Row>
        <Column
          style={{ width: '33.33%', verticalAlign: 'top', textAlign: 'center' }}
        >
          <Text style={{ fontWeight: 'bold' }}>Fast Delivery</Text>
          <Text style={{ fontSize: '14px' }}>Get your order in 2 days</Text>
        </Column>
        <Column
          style={{ width: '33.33%', verticalAlign: 'top', textAlign: 'center' }}
        >
          <Text style={{ fontWeight: 'bold' }}>Free Returns</Text>
          <Text style={{ fontSize: '14px' }}>30-day return policy</Text>
        </Column>
        <Column
          style={{ width: '33.33%', verticalAlign: 'top', textAlign: 'center' }}
        >
          <Text style={{ fontWeight: 'bold' }}>24/7 Support</Text>
          <Text style={{ fontSize: '14px' }}>We are here to help</Text>
        </Column>
      </Row>
    </Section>
  );
};
```

## Full Template Example

```tsx
import {
  Html,
  Head,
  Preview,
  Body,
  Container,
  Heading,
  Text,
  Button,
  Hr,
  Img,
  Section,
} from '@react-email/components';

interface WelcomeEmailProps {
  name: string;
}

export const WelcomeEmail = ({ name }: WelcomeEmailProps) => {
  return (
    <Html>
      <Head />
      <Preview>Welcome to our platform, {name}</Preview>
      <Body style={main}>
        <Container style={container}>
          <Img
            src="https://example.com/logo.png"
            width="150"
            height="40"
            alt="Company Logo"
            style={{ margin: '0 auto 32px', display: 'block' }}
          />
          <Heading
            style={{ fontSize: '24px', fontWeight: '600', color: '#333' }}
          >
            Welcome, {name}
          </Heading>
          <Text style={{ fontSize: '16px', lineHeight: '24px', color: '#555' }}>
            Thank you for joining. Get started by setting up your profile.
          </Text>
          <Section style={{ textAlign: 'center', margin: '32px 0' }}>
            <Button
              href="https://example.com/onboarding"
              style={{
                backgroundColor: '#5469d4',
                color: '#ffffff',
                padding: '12px 24px',
                borderRadius: '4px',
                textDecoration: 'none',
                fontWeight: '600',
              }}
            >
              Get Started
            </Button>
          </Section>
          <Hr style={{ borderColor: '#e6e6e6', margin: '32px 0' }} />
          <Text style={{ fontSize: '12px', color: '#999' }}>
            Questions? Contact us at support@example.com
          </Text>
        </Container>
      </Body>
    </Html>
  );
};

const main: React.CSSProperties = {
  backgroundColor: '#f6f6f6',
  fontFamily:
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
};

const container: React.CSSProperties = {
  maxWidth: '600px',
  margin: '0 auto',
  padding: '48px 20px',
  backgroundColor: '#ffffff',
};

export default WelcomeEmail;
```
