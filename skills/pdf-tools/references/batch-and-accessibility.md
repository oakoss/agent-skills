---
title: Batch Processing and Accessibility
description: Queue-based batch PDF processing, PDF/A archival compliance, tagged PDFs for accessibility, digital signatures, document comparison, and secure redaction
tags:
  [
    batch,
    BullMQ,
    PDF/A,
    accessibility,
    tagged-pdf,
    signatures,
    redaction,
    comparison,
    worker,
  ]
---

## Queue-Based Batch Processing

Use BullMQ for reliable queue-based PDF processing with retry logic and progress tracking:

```ts
import { Queue, Worker } from 'bullmq';
import { extractText, getDocumentProxy } from 'unpdf';

interface PdfJob {
  filePath: string;
  outputPath: string;
}

const pdfQueue = new Queue<PdfJob>('pdf-processing', {
  connection: { host: 'localhost', port: 6379 },
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 1000 },
    removeOnComplete: 100,
    removeOnFail: 500,
  },
});

const worker = new Worker<PdfJob>(
  'pdf-processing',
  async (job) => {
    const buffer = await fs.readFile(job.data.filePath);
    const pdf = await getDocumentProxy(new Uint8Array(buffer));
    const { text } = await extractText(pdf, { mergePages: true });

    await job.updateProgress(50);
    await fs.writeFile(job.data.outputPath, text);
    await job.updateProgress(100);

    return { pages: pdf.numPages, chars: text.length };
  },
  {
    connection: { host: 'localhost', port: 6379 },
    concurrency: 4,
  },
);

worker.on('failed', (job, err) => {
  console.error(`Job ${job?.id} failed: ${err.message}`);
});
```

### Enqueuing Jobs with Progress Tracking

```ts
async function processBatch(files: string[]) {
  const jobs = await pdfQueue.addBulk(
    files.map((filePath, i) => ({
      name: `extract-${i}`,
      data: { filePath, outputPath: filePath.replace('.pdf', '.txt') },
    })),
  );

  const results = await Promise.allSettled(
    jobs.map((job) => job.waitUntilFinished(queueEvents)),
  );

  const succeeded = results.filter((r) => r.status === 'fulfilled').length;
  const failed = results.filter((r) => r.status === 'rejected').length;

  return { succeeded, failed, total: files.length };
}
```

### Handling Corrupt Files

Corrupt PDFs crash parsers silently. Validate before processing:

```ts
async function validatePdf(buffer: Buffer): Promise<boolean> {
  const header = buffer.subarray(0, 5).toString('ascii');
  if (header !== '%PDF-') return false;

  try {
    await getDocumentProxy(new Uint8Array(buffer));
    return true;
  } catch {
    return false;
  }
}
```

For files that fail validation, attempt repair with qpdf before retrying:

```bash
qpdf --replace-input possibly-corrupt.pdf
```

## PDF/A Compliance

PDF/A is an ISO standard (ISO 19005) for long-term archival. It restricts features that prevent reliable reproduction: no JavaScript, no external font references, no encryption.

### Validation

```bash
# verapdf is the reference validator
verapdf --flavour 2b input.pdf

# Output includes compliance status and violations
verapdf --format json input.pdf
```

### Generating PDF/A-Compliant Documents

With Puppeteer, embed all fonts and avoid transparency:

```ts
const pdf = await page.pdf({
  format: 'A4',
  printBackground: true,
  tagged: true,
});

// Post-process with ghostscript for PDF/A-2b conversion
// gs -dPDFA=2 -dBATCH -dNOPAUSE -sDEVICE=pdfwrite
//    -sColorConversionStrategy=UseDeviceIndependentColor
//    -sOutputFile=output-pdfa.pdf input.pdf
```

```bash
gs -dPDFA=2 -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
  -sColorConversionStrategy=UseDeviceIndependentColor \
  -sOutputFile=output-pdfa.pdf input.pdf
```

### PDF/A Levels

| Level   | Requirement                                      |
| ------- | ------------------------------------------------ |
| PDF/A-1 | Based on PDF 1.4, no transparency                |
| PDF/A-2 | Based on PDF 1.7, allows JPEG2000, layers        |
| PDF/A-3 | Same as 2, plus allows embedded file attachments |

Use PDF/A-2b for most archival use cases. The "b" suffix means "basic" conformance (visual appearance only).

## Tagged PDFs for Accessibility

Tagged PDFs contain a logical structure tree that screen readers use to navigate the document. Without tags, assistive technology reads raw text in drawing order, which often scrambles multi-column layouts.

### Structure Tags

| Tag        | Purpose                     |
| ---------- | --------------------------- |
| `Document` | Root element                |
| `H1`-`H6`  | Heading levels              |
| `P`        | Paragraph                   |
| `Table`    | Table container             |
| `TR`       | Table row                   |
| `TH`/`TD`  | Table header / data cell    |
| `Figure`   | Image or illustration       |
| `L`/`LI`   | List / list item            |
| `Link`     | Hyperlink                   |
| `Span`     | Inline text with properties |

### Generating Tagged PDFs with Puppeteer

```ts
const pdf = await page.pdf({
  format: 'A4',
  tagged: true,
  printBackground: true,
});
```

The `tagged: true` option maps HTML semantic elements to PDF structure tags automatically. Ensure the source HTML uses proper semantic markup:

```html
<article>
  <h1>Annual Report</h1>
  <p>Summary of findings.</p>
  <figure>
    <img src="chart.png" alt="Revenue growth: 15% YoY increase" />
    <figcaption>Figure 1: Revenue Growth</figcaption>
  </figure>
  <table>
    <thead>
      <tr>
        <th>Quarter</th>
        <th>Revenue</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Q1</td>
        <td>$1.2M</td>
      </tr>
    </tbody>
  </table>
</article>
```

### Language Specification

Set the document language for proper screen reader pronunciation:

```html
<html lang="en"></html>
```

For mixed-language content, use `lang` attributes on individual elements:

```html
<p>The French term <span lang="fr">mise en place</span> means preparation.</p>
```

### Accessibility Validation

```bash
# PAC (PDF Accessibility Checker) for WCAG compliance
# Available at https://pac.pdf-accessibility.org

# pdfua validates PDF/UA (Universal Accessibility) compliance
verapdf --flavour ua1 input.pdf
```

## Digital Signatures

### Signing with node-signpdf

```ts
import { plainAddPlaceholder } from '@signpdf/placeholder-plain';
import { P12Signer } from '@signpdf/signer-p12';
import signpdf from '@signpdf/signpdf';

async function signDocument(
  pdfBuffer: Buffer,
  p12Buffer: Buffer,
  passphrase: string,
) {
  const pdfWithPlaceholder = plainAddPlaceholder({
    pdfBuffer,
    reason: 'Document approval',
    contactInfo: 'signer@example.com',
    name: 'Authorized Signer',
    location: 'New York, US',
  });

  const signer = new P12Signer(p12Buffer, { passphrase });
  const signedPdf = await signpdf.sign(pdfWithPlaceholder, signer);

  return signedPdf;
}
```

### Signature Verification

```ts
import { extractSignature } from '@signpdf/utils';
import * as forge from 'node-forge';

function verifySignature(signedPdfBuffer: Buffer) {
  const { signature, signedData } = extractSignature(signedPdfBuffer);

  const p7 = forge.pkcs7.messageFromAsn1(
    forge.asn1.fromDer(forge.util.createBuffer(signature)),
  );

  const cert = p7.certificates[0];
  const subject = cert.subject.getField('CN')?.value;
  const validFrom = cert.validity.notBefore;
  const validTo = cert.validity.notAfter;

  return {
    signer: subject,
    validFrom,
    validTo,
    isExpired: new Date() > validTo,
  };
}
```

### Certificate Chain Validation

Verify the signer's certificate chains to a trusted root:

```ts
function validateCertChain(
  cert: forge.pki.Certificate,
  caStore: forge.pki.CAStore,
) {
  try {
    forge.pki.verifyCertificateChain(caStore, [cert]);
    return { valid: true };
  } catch (err) {
    return { valid: false, reason: (err as Error).message };
  }
}
```

## PDF Comparison

### Text Diff Between Versions

```ts
import { extractText, getDocumentProxy } from 'unpdf';
import { diffLines } from 'diff';

async function comparePdfs(bufferA: Buffer, bufferB: Buffer) {
  const pdfA = await getDocumentProxy(new Uint8Array(bufferA));
  const pdfB = await getDocumentProxy(new Uint8Array(bufferB));

  const textA = (await extractText(pdfA, { mergePages: true })).text;
  const textB = (await extractText(pdfB, { mergePages: true })).text;

  const changes = diffLines(textA, textB);

  return changes
    .filter((c) => c.added || c.removed)
    .map((c) => ({
      type: c.added ? 'added' : 'removed',
      value: c.value.trim(),
    }));
}
```

### Visual Diff with pixelmatch

Render each page as an image and compare pixel-by-pixel:

```ts
import pixelmatch from 'pixelmatch';
import { PNG } from 'pngjs';

function visualDiff(imgA: PNG, imgB: PNG) {
  const { width, height } = imgA;
  const diff = new PNG({ width, height });

  const mismatchedPixels = pixelmatch(
    imgA.data,
    imgB.data,
    diff.data,
    width,
    height,
    { threshold: 0.1 },
  );

  const totalPixels = width * height;
  const diffPercentage = (mismatchedPixels / totalPixels) * 100;

  return { mismatchedPixels, diffPercentage, diffImage: diff };
}
```

## Redaction

### Permanent vs Visual Overlay

| Approach       | Security | What Happens                                            |
| -------------- | -------- | ------------------------------------------------------- |
| Visual overlay | Insecure | Black rectangle drawn over text; text still extractable |
| True redaction | Secure   | Content bytes removed from the PDF stream               |

Visual overlays are the most common redaction mistake. The text remains in the file and can be extracted with `pdftotext` or copy-paste.

### Secure Redaction with qpdf

```bash
# Step 1: Linearize and decompress for inspection
qpdf --qdf --object-streams=disable input.pdf decompressed.pdf

# Step 2: Apply redaction with a dedicated tool
# Python's pymupdf (fitz) performs true content removal
```

```python
import fitz

doc = fitz.open("input.pdf")
page = doc[0]

sensitive_areas = page.search_for("SSN: 123-45-6789")
for area in sensitive_areas:
    page.add_redact_annot(area, fill=(0, 0, 0))

page.apply_redactions()
doc.save("redacted.pdf")
```

The `apply_redactions()` call permanently removes the underlying text content, not just the visual layer.

### Metadata Stripping

PDFs carry metadata that may contain sensitive information:

```bash
# Remove all metadata with qpdf
qpdf --linearize --replace-input \
  --no-original-object-ids input.pdf

# Inspect metadata with exiftool
exiftool input.pdf

# Strip metadata with exiftool
exiftool -all= -overwrite_original input.pdf
```

```ts
import { PDFDocument } from 'pdf-lib';

async function stripMetadata(buffer: Buffer) {
  const pdf = await PDFDocument.load(buffer);

  pdf.setTitle('');
  pdf.setAuthor('');
  pdf.setSubject('');
  pdf.setKeywords([]);
  pdf.setProducer('');
  pdf.setCreator('');

  return Buffer.from(await pdf.save());
}
```

## Tool Selection

| Task                   | Tool               | Notes                               |
| ---------------------- | ------------------ | ----------------------------------- |
| Batch queue processing | BullMQ + unpdf     | Redis-backed, retry and concurrency |
| PDF/A validation       | verapdf            | Reference implementation            |
| PDF/A conversion       | ghostscript        | Post-process with `-dPDFA=2`        |
| Tagged PDF generation  | Puppeteer          | `tagged: true` option               |
| Digital signing        | @signpdf/\*        | PKCS#7 signatures                   |
| Text comparison        | unpdf + diff       | Structural text diff                |
| Visual comparison      | pixelmatch         | Pixel-level page diff               |
| Secure redaction       | pymupdf (fitz)     | True content removal                |
| Metadata stripping     | exiftool / pdf-lib | Remove author, title, timestamps    |
