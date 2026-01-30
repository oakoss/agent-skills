---
title: Form Filling
description: Fillable PDF form field extraction and filling with pdf-lib, non-fillable form annotation workflow with visual analysis and bounding box validation
tags:
  [forms, fillable, annotations, AcroForm, bounding-box, pdf-lib, validation]
---

## Determining Form Type

First check whether the PDF has fillable form fields:

```bash
python scripts/check_fillable_fields <file.pdf>
```

Based on the result, follow either the fillable or non-fillable workflow.

## Fillable Forms Workflow

### Step 1: Extract Field Information

```bash
python scripts/extract_form_field_info.py <input.pdf> <field_info.json>
```

This produces a JSON array describing each field:

```json
[
  {
    "field_id": "last_name",
    "page": 1,
    "rect": [100, 200, 300, 220],
    "type": "text"
  },
  {
    "field_id": "Checkbox12",
    "page": 1,
    "type": "checkbox",
    "checked_value": "/On",
    "unchecked_value": "/Off"
  },
  {
    "field_id": "gender_group",
    "page": 1,
    "type": "radio_group",
    "radio_options": [
      { "value": "/Male", "rect": [100, 300, 115, 315] },
      { "value": "/Female", "rect": [150, 300, 165, 315] }
    ]
  }
]
```

### Step 2: Visual Analysis

Convert the PDF to images and match fields to their visual purpose:

```bash
python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>
```

Analyze the images to determine what each field represents.

### Step 3: Create Field Values

Create a `field_values.json` mapping each field to its intended value:

```json
[
  {
    "field_id": "last_name",
    "description": "The user's last name",
    "page": 1,
    "value": "Simpson"
  },
  {
    "field_id": "Checkbox12",
    "description": "Checked if user is 18 or over",
    "page": 1,
    "value": "/On"
  }
]
```

### Step 4: Fill the Form

```bash
python scripts/fill_fillable_fields.py <input.pdf> <field_values.json> <output.pdf>
```

The script validates field IDs and values. Fix any errors and retry.

## Non-Fillable Forms Workflow

For PDFs without form fields, create text annotations at visual positions.

### Step 1: Visual Analysis

Convert to images and identify all form areas:

```bash
python scripts/convert_pdf_to_images.py <file.pdf> <output_directory>
```

For each field, determine bounding boxes for both the label and the entry area. Label and entry bounding boxes must not intersect.

Common form layouts:

| Layout                              | Entry Area Location             |
| ----------------------------------- | ------------------------------- |
| Label inside box (`Name: ____`)     | Right of label, to edge of box  |
| Label before line (`Email: ___`)    | Above the line, full width      |
| Label under line (line then `Name`) | Above the line, full width      |
| Checkboxes (`Yes [] No []`)         | Small square only, not the text |

### Step 2: Create fields.json

```json
{
  "pages": [{ "page_number": 1, "image_width": 1700, "image_height": 2200 }],
  "form_fields": [
    {
      "page_number": 1,
      "description": "Last name entry",
      "field_label": "Last name",
      "label_bounding_box": [30, 125, 95, 142],
      "entry_bounding_box": [100, 125, 280, 142],
      "entry_text": {
        "text": "Johnson",
        "font_size": 14,
        "font_color": "000000"
      }
    },
    {
      "page_number": 1,
      "description": "Age verification checkbox",
      "field_label": "Yes",
      "label_bounding_box": [100, 525, 132, 540],
      "entry_bounding_box": [140, 525, 155, 540],
      "entry_text": { "text": "X" }
    }
  ]
}
```

### Step 3: Generate and Validate

Create validation images with colored overlays:

```bash
python scripts/create_validation_image.py <page> <fields.json> <input_image> <output_image>
```

Red rectangles mark entry areas, blue rectangles mark labels. Run the automated check:

```bash
python scripts/check_bounding_boxes.py <fields.json>
```

Visually inspect the validation images:

- Red rectangles must only cover input areas (no text)
- Blue rectangles should contain label text
- For checkboxes: red rectangle centered on the checkbox square

Iterate until all bounding boxes are correct.

### Step 4: Fill the Form

```bash
python scripts/fill_pdf_form_with_annotations.py <input.pdf> <fields.json> <output.pdf>
```

## Common Issues

| Issue                         | Fix                                                              |
| ----------------------------- | ---------------------------------------------------------------- |
| Field IDs not matching        | Extract field info again; use exact `field_id` values            |
| Flattened form fields         | Fields cannot be filled; use annotation workflow instead         |
| Overlapping bounding boxes    | Re-analyze images; ensure label and entry boxes do not intersect |
| Text too large for entry area | Reduce `font_size` in `entry_text`                               |
| Checkbox not rendering        | Use the exact `checked_value` from field info                    |
