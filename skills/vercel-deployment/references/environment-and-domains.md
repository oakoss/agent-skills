---
title: Environment Variables and Domains
description: Environment variables across production/preview/development, system variables, custom domains, DNS configuration, and branch deployments
tags:
  [
    environment-variables,
    domains,
    dns,
    preview,
    production,
    branch-deployments,
    staging,
  ]
---

# Environment Variables and Domains

## Environment Variables

Vercel environment variables are scoped to three environments: **Production**, **Preview**, and **Development**. Set them in the dashboard under Project Settings > Environment Variables, or via the CLI.

### Adding Variables via Dashboard

Select which environments a variable applies to. A variable can apply to one, two, or all three environments.

| Environment | When Used                                                  |
| ----------- | ---------------------------------------------------------- |
| Production  | Deployments from the production branch (usually `main`)    |
| Preview     | Deployments from non-production branches and pull requests |
| Development | Local development via `vercel dev` or `vercel env pull`    |

### Adding Variables via CLI

```bash
vercel env add DATABASE_URL production
vercel env add DATABASE_URL production preview
vercel env add NEXT_PUBLIC_API_URL production preview development
```

Remove a variable:

```bash
vercel env rm DATABASE_URL production
```

List all variables:

```bash
vercel env ls
```

### Pulling Variables for Local Development

Pull development environment variables into a local `.env` file:

```bash
vercel env pull .env.local
```

This downloads all variables scoped to the Development environment. Share with teammates who have project access.

### System Environment Variables

Vercel automatically provides system variables during builds and at runtime:

| Variable                        | Description                                                        |
| ------------------------------- | ------------------------------------------------------------------ |
| `VERCEL`                        | Always `"1"` when running on Vercel                                |
| `VERCEL_ENV`                    | `"production"`, `"preview"`, or `"development"`                    |
| `VERCEL_URL`                    | Deployment URL without protocol (e.g., `my-app-abc123.vercel.app`) |
| `VERCEL_PROJECT_PRODUCTION_URL` | Stable production domain (e.g., `my-app.vercel.app`)               |
| `VERCEL_BRANCH_URL`             | Branch-specific URL (e.g., `my-app-git-feature.vercel.app`)        |
| `VERCEL_GIT_COMMIT_SHA`         | Git commit hash                                                    |
| `VERCEL_GIT_COMMIT_REF`         | Git branch name                                                    |
| `VERCEL_GIT_REPO_SLUG`          | Repository name                                                    |

`VERCEL_URL` does not include the protocol. Always prepend `https://`:

```ts
const baseUrl = process.env.VERCEL_URL
  ? `https://${process.env.VERCEL_URL}`
  : 'http://localhost:3000';
```

For a stable production URL, prefer `VERCEL_PROJECT_PRODUCTION_URL` over `VERCEL_URL` (which changes per deployment).

### Next.js and NODE_ENV

`NODE_ENV` is always `"production"` on Vercel deployments, including preview. This is by design. Do not use `NODE_ENV` to distinguish between preview and production. Use `VERCEL_ENV` instead:

```ts
const isProduction = process.env.VERCEL_ENV === 'production';
const isPreview = process.env.VERCEL_ENV === 'preview';
```

### Sensitive Variables

Prefix variables with `NEXT_PUBLIC_` (Next.js) or `VITE_` (Vite) only if they should be exposed to the browser. API keys and secrets should never use these prefixes.

```text
NEXT_PUBLIC_API_URL=https://api.example.com    # Exposed to browser
DATABASE_URL=postgresql://...                    # Server-only
STRIPE_SECRET_KEY=sk_live_...                    # Server-only
```

## Custom Domains

### Adding a Domain

Navigate to Project Settings > Domains and add your domain. Vercel provides DNS configuration instructions.

### DNS Configuration

Two approaches depending on your DNS provider:

**Option A: External DNS (recommended for existing DNS)**

For apex domains (e.g., `example.com`), add an A record:

```text
Type: A
Name: @
Value: 76.76.21.21
```

For subdomains (e.g., `www.example.com`, `app.example.com`), add a CNAME:

```text
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

**Option B: Vercel Nameservers (required for wildcard domains)**

Point your domain registrar to Vercel nameservers:

```text
ns1.vercel-dns.com
ns2.vercel-dns.com
```

Migrate any existing DNS records to Vercel before switching nameservers.

### Adding Both Apex and www

Always add both `example.com` and `www.example.com`. Configure one as the primary domain and the other as a redirect:

```text
example.com        → Primary
www.example.com    → Redirects to example.com
```

Vercel does not auto-add the `www` variant. Omitting it causes 404 errors for users who type `www.`.

### Domain per Environment

Assign custom domains to specific environments for staging workflows:

```text
app.example.com        → Production
staging.example.com    → Preview (staging branch)
```

Configure branch-specific domains in Project Settings > Domains by selecting the target environment and branch.

## Branch Deployments

### Preview URLs

Every push to a non-production branch generates a unique preview URL:

```text
my-app-<hash>-team.vercel.app           # Unique per commit
my-app-git-feature-branch-team.vercel.app  # Stable per branch
```

Preview deployments use Preview environment variables automatically.

### Staging Environment

Create a staging workflow with custom environments:

1. Create a custom environment (e.g., "Staging") in Project Settings > Environments
2. Set branch rules to match your staging branch (e.g., `staging`)
3. Assign a custom domain (e.g., `staging.example.com`)
4. Configure environment-specific variables

Deployments to the `staging` branch automatically use the Staging environment configuration.

### Staged Production Deployments

Deploy to production without immediately going live:

1. Disable "Auto-assign Custom Production Domains" in Branch Tracking settings
2. Deploy to production — the build runs but domains are not updated
3. Verify the deployment at its unique URL
4. Promote manually via dashboard or CLI: `vercel promote <deployment-url>`

### Protection and Access

Restrict preview deployments to authenticated users:

```json
{
  "git": {
    "deploymentEnabled": {
      "main": true,
      "staging": true
    }
  }
}
```

Enable Vercel Authentication or password protection for preview URLs in Project Settings > Deployment Protection.
