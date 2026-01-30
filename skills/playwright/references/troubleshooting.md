---
title: Troubleshooting
description: Solutions for common Playwright problems including missing executables, Docker performance, blank screenshots, page crashes, captchas, and Ubuntu compatibility
tags:
  [
    troubleshooting,
    error,
    executable,
    Docker,
    shm,
    screenshot,
    crash,
    captcha,
    Ubuntu,
    setup,
    checklist,
  ]
---

# Troubleshooting

## "Executable doesn't exist" Error

```bash
npx playwright install chromium
# Or for all browsers:
npx playwright install
```

## Slow Performance in Docker

Add shared memory size:

```dockerfile
RUN playwright install --with-deps chromium
```

```bash
docker run --shm-size=2gb your-image
```

## Blank Screenshots

Wait for content to load before capturing:

```typescript
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForTimeout(1000); // Extra buffer for lazy-loaded content
await page.screenshot({ path: 'output.png' });
```

## "Page crashed" Errors

Reduce concurrency or add memory:

```typescript
const browser = await chromium.launch({
  args: ['--disable-dev-shm-usage'], // Use /tmp instead of /dev/shm
});
```

## Captcha Always Appears

1. Verify stealth mode is active (check `bot.sannysoft.com`)
2. Rotate user agents
3. Add random delays between actions
4. Use residential proxy if needed

## Ubuntu 25.10 Installation Fails

**Error:** `Unable to locate package libicu74`, `Package 'libxml2' has no installation candidate`
**Source:** [GitHub Issue #38874](https://github.com/microsoft/playwright/issues/38874)

```bash
# Use Ubuntu 24.04 Docker image (officially supported)
docker pull mcr.microsoft.com/playwright:v1.57.0-noble

# Temporary workaround (if Docker not an option)
sudo apt-get update
sudo apt-get install libicu72 libxml2
```

## Setup Checklist

- [ ] Playwright installed (`npm list playwright` or `pip show playwright`)
- [ ] Browsers downloaded (`npx playwright install chromium`)
- [ ] Basic script runs successfully
- [ ] Stealth mode configured (if needed)
- [ ] Session persistence works
- [ ] Screenshots save correctly
- [ ] Error handling includes retries
- [ ] Browser closes properly (no zombie processes)
- [ ] Tested with `headless: false` first
- [ ] Production script uses `headless: true`
