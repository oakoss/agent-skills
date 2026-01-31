---
title: High-Fidelity Generation
description: Puppeteer HTML-to-PDF conversion, React template rendering, CSS print tips, page headers and footers, and browser pool optimization
tags: [generation, Puppeteer, HTML-to-PDF, CSS, print, React, templates]
---

## Puppeteer HTML-to-PDF

Generate PDFs from React components for visual consistency with the web app:

```ts
import puppeteer from 'puppeteer';

export async function POST(req: Request) {
  const { htmlContent } = await req.json();
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
  const pdfBuffer = await page.pdf({
    format: 'A4',
    printBackground: true,
    margin: { top: '20px', bottom: '20px' },
  });

  await browser.close();
  return new Response(pdfBuffer, {
    headers: { 'Content-Type': 'application/pdf' },
  });
}
```

## React Template Rendering

Render React components to HTML, then convert to PDF:

```tsx
import puppeteer from 'puppeteer';
import { renderToString } from 'react-dom/server';

export async function createPdfFromReact(Component, props) {
  const html = renderToString(<Component {...props} />);
  const tailwindCss = await fs.readFile('./public/pdf.css', 'utf-8');

  const fullHtml = `
    <html>
      <head><style>${tailwindCss}</style></head>
      <body>${html}</body>
    </html>
  `;

  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setContent(fullHtml, { waitUntil: 'networkidle0' });

  const pdf = await page.pdf({
    format: 'A4',
    displayHeaderFooter: true,
    footerTemplate:
      '<span style="font-size: 10px; margin-left: 20px;">Page <span class="pageNumber"></span></span>',
  });

  await browser.close();
  return pdf;
}
```

## CSS Print Tips

| Property                | Purpose                                         |
| ----------------------- | ----------------------------------------------- |
| `break-inside: avoid`   | Prevents table rows from splitting across pages |
| `@page { margin: 1cm }` | Sets explicit PDF margins                       |
| `break-before: page`    | Forces a page break before an element           |
| `box-decoration-break`  | Controls decoration behavior at page breaks     |

For professional printing, consider CMYK color profiles in CSS.

## Playwright Equivalent

Playwright uses `networkidle` instead of Puppeteer's `networkidle0`. Playwright does not support `networkidle2`. The `page.pdf()` API is otherwise identical:

```ts
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(url, { waitUntil: 'networkidle' });
const pdfBuffer = await page.pdf({ format: 'A4', printBackground: true });
await browser.close();
```

## Font Handling in Containers

System fonts may not be available in Docker or serverless environments:

- Embed Google Fonts via `<link>` or inline CSS
- Bundle WOFF2 files in the project and load via `@font-face`
- Ensure `waitUntil: 'networkidle0'` (Puppeteer) or `'networkidle'` (Playwright) to allow font loading

## Browser Pool Optimization

Launching a browser takes approximately 500ms. In high-traffic APIs:

- Keep a pool of pre-warmed Puppeteer instances
- Use a dedicated PDF-sidecar service
- Reuse browser instances across requests (manage page lifecycle instead)

## Troubleshooting

| Issue          | Cause                         | Fix                                                          |
| -------------- | ----------------------------- | ------------------------------------------------------------ |
| Missing fonts  | System fonts not in container | Embed Google Fonts or WOFF2                                  |
| Huge file size | High-res images not optimized | Compress with ghostscript or pdf-lib                         |
| Blank pages    | Content not loaded before PDF | Use `networkidle0` (Puppeteer) or `networkidle` (Playwright) |
| Wrong margins  | Default browser margins       | Set explicit `margin` in `page.pdf()` options                |
