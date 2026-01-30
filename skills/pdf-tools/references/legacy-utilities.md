---
title: Legacy Utilities
description: Python PDF tools (pdfplumber, pypdf) and CLI utilities (qpdf, poppler-utils) for batch processing, table extraction, and forensic repairs
tags: [pdfplumber, pypdf, qpdf, poppler, Python, CLI, batch-processing]
---

## Python Tools

### pdfplumber (Table Specialist)

For non-AI table extraction, pdfplumber is the most precise tool for identifying cell boundaries:

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("complex_report.pdf") as pdf:
    table = pdf.pages[0].extract_table()
    df = pd.DataFrame(table[1:], columns=table[0])
```

Best for: Multi-column layouts, bordered tables, precise cell boundary detection.

### pypdf (Fast Merging)

For merging thousands of files, pypdf is significantly lighter than a headless browser:

```python
from pypdf import PdfWriter

writer = PdfWriter()
for pdf in ["a.pdf", "b.pdf"]:
    writer.append(pdf)
writer.write("combined.pdf")
```

Best for: Bulk merge/split operations, metadata extraction, simple text extraction.

## CLI Forensics

### qpdf (Repair and Security)

If a PDF is corrupted or has unreadable metadata, qpdf is the go-to tool:

```bash
# Decompress a PDF to inspect raw objects (human readable)
qpdf --qdf --object-streams=disable input.pdf inspect.pdf

# Fix a "Premature EOF" error
qpdf input.pdf --replace-input

# AES-256 encryption
qpdf --encrypt user-pass owner-pass 256 -- input.pdf secured.pdf
```

### poppler-utils (Fast Extraction)

When raw text is needed quickly for search indexing:

```bash
# Fast text extraction preserving layout
pdftotext -layout input.pdf -

# Extract with UTF-8 encoding for garbled text
pdftotext -enc UTF-8 input.pdf output.txt
```

## Tool Selection Guide

| Scenario                 | Recommended Tool                 |
| ------------------------ | -------------------------------- |
| Next.js API route        | JS: pdf-lib, Puppeteer           |
| Heavy batch processing   | Python: pdfplumber, or CLI: qpdf |
| AI RAG pipeline          | unpdf or pdftotext               |
| Corrupted PDF repair     | qpdf                             |
| Merge/split operations   | pypdf (Python) or pdf-lib (JS)   |
| Table extraction (no AI) | pdfplumber                       |
| Fast text for indexing   | poppler-utils                    |

## Troubleshooting

| Issue                 | Tool        | Fix                                         |
| --------------------- | ----------- | ------------------------------------------- |
| Garbled text          | poppler     | Use `-enc UTF-8` flag                       |
| Corrupted structure   | qpdf        | `qpdf input.pdf --replace-input`            |
| Missing table borders | pdfplumber  | Use `extract_table()` with custom settings  |
| Huge file size        | ghostscript | `gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook` |
