---
title: Image Upload
description: Image upload pattern with base64 preview, background upload to R2/S3, and URL replacement to prevent database bloat
tags: [tiptap, image, upload, r2, s3, base64, cloudflare]
---

# Image Upload

## Pattern: Base64 Preview → Upload → URL Replace

1. Create base64 preview for immediate display
2. Insert preview into editor
3. Upload to R2/S3 in background
4. Replace base64 with permanent URL

```ts
import { Editor } from '@tiptap/core';

async function uploadImageToR2(editor: Editor, file: File): Promise<string> {
  const reader = new FileReader();
  const base64 = await new Promise<string>((resolve) => {
    reader.onload = () => resolve(reader.result as string);
    reader.readAsDataURL(file);
  });

  editor.chain().focus().setImage({ src: base64 }).run();

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData,
  });

  const { url } = await response.json();

  editor.chain().focus().updateAttributes('image', { src: url }).run();

  return url;
}
```

## Image Extension Configuration

Always disable base64 to prevent bloat:

```ts
import Image from '@tiptap/extension-image';

Image.configure({
  inline: true,
  allowBase64: false,
  resize: {
    enabled: true,
    directions: ['top-right', 'bottom-right', 'bottom-left', 'top-left'],
    minWidth: 100,
    minHeight: 100,
    alwaysPreserveAspectRatio: true,
  },
});
```

## Why This Pattern

- Immediate user feedback (base64 preview appears instantly)
- No database bloat from base64 strings
- Works with any object storage (Cloudflare R2, AWS S3, etc.)
- Graceful error handling — if upload fails, preview is still visible
