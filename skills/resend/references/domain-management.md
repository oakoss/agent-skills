---
title: Domain Management
description: Domain verification, DNS record configuration, custom domains, sender identities, and region selection with the Resend API
tags: [domains, dns, spf, dkim, dmarc, verification, sender-identity, region]
---

# Domain Management

## Why Use a Subdomain

Resend recommends using a subdomain (e.g., `send.yourdomain.com`) instead of the root domain for email sending. This isolates your transactional email reputation from your main domain and clearly communicates the purpose of each subdomain.

## Create a Domain

```ts
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.domains.create({
  name: 'send.acme.com',
});

if (error) {
  console.error('Failed to create domain:', error);
  return;
}

console.log('Domain created:', data.id);
console.log('DNS records to configure:', data.records);
```

## Create Domain with Options

```ts
const { data, error } = await resend.domains.create({
  name: 'send.acme.com',
  region: 'eu-west-1',
  open_tracking: true,
  click_tracking: true,
  tls: 'enforced',
});
```

### Available Regions

| Region             | Value            |
| ------------------ | ---------------- |
| US East (Virginia) | `us-east-1`      |
| EU West (Ireland)  | `eu-west-1`      |
| South America      | `sa-east-1`      |
| Asia Pacific       | `ap-northeast-1` |

## DNS Records

After creating a domain, Resend returns DNS records that must be configured with your DNS provider. Three record types are required for full verification.

### SPF Record (TXT)

Authorizes Resend to send emails on behalf of your domain.

```text
Type:  TXT
Name:  send
Value: "v=spf1 include:amazonses.com ~all"
TTL:   Auto
```

### DKIM Record (TXT)

Public key used to verify email authenticity.

```text
Type:  TXT
Name:  resend._domainkey
Value: p=MIGfMA0GCSqGSIb3DQEBA... (provided by Resend)
TTL:   Auto
```

### MX Record

Routes bounce and feedback notifications.

```text
Type:     MX
Name:     send
Value:    feedback-smtp.us-east-1.amazonses.com
Priority: 10
TTL:      Auto
```

### DMARC Record (Optional, Recommended)

Add after SPF and DKIM verify to improve deliverability and prevent spoofing.

```text
Type:  TXT
Name:  _dmarc
Value: "v=DMARC1; p=none; rua=mailto:dmarc@acme.com"
TTL:   Auto
```

DMARC policy values:

- `p=none` — Monitor only (start here)
- `p=quarantine` — Send suspicious emails to spam
- `p=reject` — Reject emails that fail authentication

## Verify a Domain

Trigger a DNS verification check after configuring records.

```ts
const { data, error } = await resend.domains.verify('domain_id_123');

if (error) {
  console.error('Verification failed:', error);
  return;
}

console.log('Verification initiated');
```

## List Domains

```ts
const { data, error } = await resend.domains.list();

if (data) {
  for (const domain of data.data) {
    console.log(`${domain.name}: ${domain.status}`);
  }
}
```

## Get Domain Details

```ts
const { data, error } = await resend.domains.get('domain_id_123');

if (data) {
  console.log('Domain:', data.name);
  console.log('Status:', data.status);
  console.log('Records:', data.records);
}
```

## Update Domain Settings

```ts
const { data, error } = await resend.domains.update({
  id: 'domain_id_123',
  open_tracking: true,
  click_tracking: false,
  tls: 'enforced',
});
```

## Delete a Domain

```ts
const { data, error } = await resend.domains.remove('domain_id_123');
```

## Domain Status Values

| Status              | Description                                    |
| ------------------- | ---------------------------------------------- |
| `not_started`       | Domain created, DNS records not yet configured |
| `pending`           | DNS records detected, verification in progress |
| `verified`          | All DNS records verified, ready to send        |
| `failed`            | Verification failed, check DNS configuration   |
| `temporary_failure` | Transient issue, will retry automatically      |

## REST API (cURL)

### Create Domain

```bash
curl -X POST 'https://api.resend.com/domains' \
  -H 'Authorization: Bearer re_xxxxxxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "send.acme.com"
  }'
```

### Verify Domain

```bash
curl -X POST 'https://api.resend.com/domains/domain_id_123/verify' \
  -H 'Authorization: Bearer re_xxxxxxxxx'
```

### List Domains

```bash
curl -X GET 'https://api.resend.com/domains' \
  -H 'Authorization: Bearer re_xxxxxxxxx'
```

## Common Verification Issues

### Records Not Propagating

DNS changes can take up to 72 hours to propagate. Use a DNS lookup tool to confirm records are publicly visible before triggering verification.

### Incorrect Record Location

SPF and MX records must be configured on the subdomain (e.g., `send.acme.com`), not the root domain. The `Name` field in the DNS record should be `send`, not `@` or blank.

### Conflicting SPF Records

Only one SPF record is allowed per domain. If an existing SPF record exists, merge the Resend include:

```text
"v=spf1 include:_spf.google.com include:amazonses.com ~all"
```

### Cloudflare DNS Proxy

If using Cloudflare, set the DNS records to "DNS only" (gray cloud), not "Proxied" (orange cloud). Proxied records can interfere with email verification.

## Sender Identity Best Practices

- Use a consistent `from` address format: `"Display Name <email@send.acme.com>"`
- Match the sending domain to a verified domain
- Use different subdomains for different email types (e.g., `send.acme.com` for transactional, `news.acme.com` for marketing)
- Set `reply_to` to an address you actively monitor
