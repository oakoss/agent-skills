---
title: Styling and Layout
description: Inline CSS styles, Tailwind CSS integration, custom fonts, responsive patterns, and dark mode
tags:
  [
    inline-styles,
    Tailwind,
    Font,
    responsive,
    dark-mode,
    CSS,
    media-queries,
    web-fonts,
  ]
---

# Styling and Layout

## Inline Styles

Email clients strip `<style>` tags and ignore external stylesheets. Inline styles are the most reliable approach.

### Style Objects

Define reusable style objects with `React.CSSProperties` for type safety.

```tsx
import { Html, Body, Container, Text, Heading } from '@react-email/components';

export const StyledEmail = () => {
  return (
    <Html>
      <Body style={main}>
        <Container style={container}>
          <Heading style={heading}>Order Confirmed</Heading>
          <Text style={text}>Your order has been placed successfully.</Text>
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
  borderRadius: '8px',
};

const heading: React.CSSProperties = {
  fontSize: '24px',
  fontWeight: '600',
  color: '#111111',
  margin: '0 0 16px',
};

const text: React.CSSProperties = {
  fontSize: '16px',
  lineHeight: '24px',
  color: '#555555',
  margin: '0 0 24px',
};
```

### Email-Safe CSS Properties

Not all CSS properties work across email clients. Stick to well-supported properties.

| Supported                           | Avoid                                 |
| ----------------------------------- | ------------------------------------- |
| `background-color`                  | `background` shorthand with gradients |
| `color`, `font-size`, `font-family` | `gap`, `grid`, `flex`                 |
| `padding`, `margin`                 | `position: absolute/fixed`            |
| `border`, `border-radius`           | `box-shadow` (limited support)        |
| `text-align`, `vertical-align`      | `float` (inconsistent)                |
| `width`, `max-width`, `height`      | `calc()` (limited)                    |
| `display: block/inline-block`       | `display: flex/grid`                  |
| `table-layout`                      | `overflow`                            |

### Font Stack

Use a web-safe font stack as the base. Custom fonts are additive.

```tsx
const fontStack =
  "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";
```

## Tailwind CSS

The `Tailwind` component enables utility classes by inlining Tailwind styles at render time. It wraps the `Html` component.

### Basic Tailwind Usage

```tsx
import {
  Html,
  Body,
  Container,
  Text,
  Heading,
  Tailwind,
} from '@react-email/components';

export const TailwindEmail = () => {
  return (
    <Tailwind>
      <Html>
        <Body className="bg-gray-100 font-sans">
          <Container className="mx-auto my-8 max-w-xl bg-white p-8 rounded-lg">
            <Heading className="text-2xl font-bold text-gray-900 mb-4">
              Welcome
            </Heading>
            <Text className="text-base text-gray-600 leading-relaxed">
              Thanks for signing up.
            </Text>
          </Container>
        </Body>
      </Html>
    </Tailwind>
  );
};
```

### Custom Tailwind Config

Pass a `config` prop to extend Tailwind with custom colors, spacing, or fonts.

```tsx
import {
  Html,
  Body,
  Container,
  Button,
  Text,
  Tailwind,
} from '@react-email/components';

export const BrandedEmail = () => {
  return (
    <Tailwind
      config={{
        theme: {
          extend: {
            colors: {
              brand: '#5469d4',
              'brand-dark': '#3451b2',
            },
            spacing: {
              '18': '4.5rem',
            },
          },
        },
      }}
    >
      <Html>
        <Body className="bg-gray-50 font-sans">
          <Container className="mx-auto my-8 p-8 bg-white rounded-lg max-w-2xl">
            <Text className="text-base text-gray-700 mb-6">
              Click below to get started.
            </Text>
            <Button
              href="https://example.com"
              className="bg-brand text-white font-semibold py-3 px-6 rounded-md no-underline"
            >
              Get Started
            </Button>
          </Container>
        </Body>
      </Html>
    </Tailwind>
  );
};
```

### Tailwind vs Inline Styles

Do not mix `className` and `style` on the same element. Pick one approach per component.

```tsx
// Correct: Tailwind only
<Text className="text-base text-gray-700 mb-4">Content</Text>

// Correct: Inline only
<Text style={{ fontSize: '16px', color: '#555', marginBottom: '16px' }}>Content</Text>

// Avoid: Mixed on same element
<Text className="text-base" style={{ color: '#555' }}>Content</Text>
```

## Custom Fonts

Use the `Font` component inside `Head` to load web fonts. Always provide a `fallbackFontFamily`.

```tsx
import { Html, Head, Body, Font, Text } from '@react-email/components';

export const CustomFontEmail = () => {
  return (
    <Html>
      <Head>
        <Font
          fontFamily="Inter"
          fallbackFontFamily="Helvetica"
          webFont={{
            url: 'https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiA.woff2',
            format: 'woff2',
          }}
          fontWeight={400}
          fontStyle="normal"
        />
        <Font
          fontFamily="Inter"
          fallbackFontFamily="Helvetica"
          webFont={{
            url: 'https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuBWYAZ9hiA.woff2',
            format: 'woff2',
          }}
          fontWeight={700}
          fontStyle="normal"
        />
      </Head>
      <Body style={{ fontFamily: 'Inter, Helvetica, Arial, sans-serif' }}>
        <Text style={{ fontWeight: 400 }}>Regular weight text</Text>
        <Text style={{ fontWeight: 700 }}>Bold weight text</Text>
      </Body>
    </Html>
  );
};
```

### Font Props

| Prop                 | Type              | Required | Description                                                 |
| -------------------- | ----------------- | -------- | ----------------------------------------------------------- |
| `fontFamily`         | `string`          | Yes      | Font name to register                                       |
| `fallbackFontFamily` | `string`          | Yes      | Web-safe fallback (e.g., `Verdana`, `Georgia`, `Helvetica`) |
| `webFont`            | `{ url, format }` | No       | URL and format (`woff2`, `woff`) of the web font file       |
| `fontWeight`         | `number`          | No       | Font weight (e.g., `400`, `700`)                            |
| `fontStyle`          | `string`          | No       | Font style (`normal`, `italic`)                             |

Load one `Font` component per weight/style combination.

## Responsive Patterns

Email clients have limited support for `@media` queries. Use these patterns for responsive layouts.

### Fluid Width

Use percentage widths with a `max-width` constraint.

```tsx
import { Container, Section, Row, Column, Text } from '@react-email/components';

const Email = () => {
  return (
    <Container style={{ maxWidth: '600px', width: '100%', margin: '0 auto' }}>
      <Section>
        <Row>
          <Column style={{ width: '50%', paddingRight: '8px' }}>
            <Text>Left column</Text>
          </Column>
          <Column style={{ width: '50%', paddingLeft: '8px' }}>
            <Text>Right column</Text>
          </Column>
        </Row>
      </Section>
    </Container>
  );
};
```

### Single Column for Mobile

For critical content, use a single-column layout that works on all screen sizes.

```tsx
import { Container, Text, Button } from '@react-email/components';

const Email = () => {
  return (
    <Container
      style={{
        maxWidth: '480px',
        width: '100%',
        margin: '0 auto',
        padding: '0 16px',
      }}
    >
      <Text style={{ fontSize: '16px', lineHeight: '24px' }}>
        A narrower container naturally reads well on mobile without media
        queries.
      </Text>
      <Button
        href="https://example.com"
        style={{
          display: 'block',
          width: '100%',
          textAlign: 'center',
          backgroundColor: '#5469d4',
          color: '#ffffff',
          padding: '12px',
          borderRadius: '4px',
          textDecoration: 'none',
        }}
      >
        Full Width Button
      </Button>
    </Container>
  );
};
```

## Dark Mode

Email client dark mode support varies. Use these strategies for consistent appearance.

### Meta Tag Approach

Add a `color-scheme` meta tag in `Head` to indicate dark mode support.

```tsx
import { Html, Head, Body, Container, Text } from '@react-email/components';

export const DarkModeEmail = () => {
  return (
    <Html>
      <Head>
        <meta name="color-scheme" content="light dark" />
        <meta name="supported-color-schemes" content="light dark" />
      </Head>
      <Body style={{ backgroundColor: '#ffffff', color: '#111111' }}>
        <Container>
          <Text>This email supports dark mode detection.</Text>
        </Container>
      </Body>
    </Html>
  );
};
```

### Dark Mode Safe Colors

Choose colors that remain legible in both light and dark modes. Avoid pure white (`#ffffff`) backgrounds for inner containers and pure black (`#000000`) text when possible.

| Element    | Light Mode | Dark Mode Safe                   |
| ---------- | ---------- | -------------------------------- |
| Background | `#ffffff`  | `#f6f6f6` (slightly off-white)   |
| Text       | `#000000`  | `#111111` or `#333333`           |
| Links      | `#0066cc`  | `#5469d4` (higher contrast blue) |
| Borders    | `#e6e6e6`  | `#cccccc`                        |

### Tailwind Dark Mode

The Tailwind component supports `dark:` variants that target email clients with dark mode.

```tsx
import { Html, Body, Text, Tailwind } from '@react-email/components';

export const DarkModeTailwind = () => {
  return (
    <Tailwind>
      <Html>
        <Body className="bg-white dark:bg-gray-900">
          <Text className="text-gray-900 dark:text-gray-100">
            Adapts to dark mode in supporting email clients.
          </Text>
        </Body>
      </Html>
    </Tailwind>
  );
};
```

Not all email clients support `dark:` variants. Always ensure your base (light) styles are readable.
