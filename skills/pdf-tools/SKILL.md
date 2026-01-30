---
name: pdf-tools
description: 'PDF engineering for extraction, generation, modification, and form filling. Use when extracting text or tables from PDFs, generating PDFs with Puppeteer, modifying PDFs with pdf-lib, filling PDF forms, or implementing PDF security. Use for AI-assisted OCR, HTML-to-PDF conversion, and document processing pipelines.'
---

# PDF Tools

Full-lifecycle PDF engineering covering extraction, generation, modification, form filling, and security. Prioritizes JavaScript-first solutions (pdf-lib, unpdf, Puppeteer) with Python/CLI utilities for advanced scenarios.

**When to use**: Extracting structured data from PDFs, generating pixel-perfect PDFs from HTML/React, modifying existing PDFs, filling forms (fillable or non-fillable), or securing documents with encryption.

**When NOT to use**: Simple text file processing, image-only manipulation without PDF context, or tasks better handled by a word processor.

## Quick Reference

| Task                       | Tool                      | Key Point                                     |
| -------------------------- | ------------------------- | --------------------------------------------- |
| Generate PDF from HTML     | Puppeteer / Playwright    | `page.pdf()` with `waitUntil: 'networkidle0'` |
| Extract text (lightweight) | unpdf                     | Edge/serverless compatible                    |
| Extract tables (AI)        | Vision model + Zod schema | Multi-column and merged cell support          |
| Extract tables (non-AI)    | pdfplumber (Python)       | Precise cell boundary detection               |
| Modify, merge, split       | pdf-lib                   | Byte-level PDF manipulation in JS             |
| Fill fillable forms        | pdf-lib                   | Inspect AcroForm fields before writing        |
| Fill non-fillable forms    | Python annotation scripts | Visual analysis + bounding box annotations    |
| Encrypt PDF                | qpdf                      | AES-256: `qpdf --encrypt user owner 256 --`   |
| Repair corrupted PDF       | qpdf                      | `qpdf input.pdf --replace-input`              |
| Fast text extraction (CLI) | poppler-utils             | `pdftotext -layout input.pdf -`               |
| Merge thousands of files   | pypdf (Python)            | Lighter than headless browser                 |

## Common Mistakes

| Mistake                                                | Correct Pattern                                                   |
| ------------------------------------------------------ | ----------------------------------------------------------------- |
| Using canvas drawing commands for PDF generation       | Use Puppeteer/Playwright with HTML/CSS templates                  |
| Running Puppeteer in edge/serverless environments      | Use unpdf for edge; Puppeteer requires full Node.js               |
| Extracting complex layouts with basic text parsers     | Use AI-assisted OCR or pdfplumber for multi-column text           |
| Storing unencrypted PDFs with PII in public storage    | Apply AES-256 encryption via qpdf before storage                  |
| Relying on `window.print()` for server-side generation | Use headless browser APIs (`page.pdf()`) for deterministic output |
| Using pypdf for complex layout extraction              | Use pdfplumber or AI OCR for multi-column or overlapping text     |
| Skipping font embedding in containerized environments  | Embed Google Fonts or WOFF2 files with Puppeteer                  |
| Writing to flattened PDF form fields                   | Inspect AcroForm fields with pdf-lib before writing               |

## Delegation

- **Inspect PDF structure and diagnose extraction issues**: Use `Explore` agent to examine AcroForm fields, encoding, and metadata
- **Build end-to-end document processing pipelines**: Use `Task` agent to implement extraction, transformation, and generation workflows
- **Design PDF architecture for a new system**: Use `Plan` agent to select tools and plan extraction, generation, or modification strategies

## References

- [AI Extraction Patterns](references/ai-extraction-patterns.md) -- Vision-based table extraction, recursive summarization, multi-pass verification
- [High-Fidelity Generation](references/high-fidelity-generation.md) -- Puppeteer HTML-to-PDF, CSS print tips, React templates, browser pooling
- [Legacy Utilities](references/legacy-utilities.md) -- pdfplumber, pypdf, qpdf, poppler-utils for batch and forensic tasks
- [Form Filling](references/form-filling.md) -- Fillable field extraction, non-fillable annotation workflow, validation scripts
