---
title: Multimodal Prompting
description: Techniques for prompting vision-language models with images and text, contextual prompting, cross-modal alignment, and best practices for image analysis tasks
tags:
  [
    multimodal,
    vision,
    image-prompting,
    VLM,
    cross-modal,
    contextual,
    image-analysis,
  ]
---

## Multimodal Prompting Overview

Modern LLMs (GPT-4o, Claude, Gemini) accept images alongside text, enabling tasks like visual question answering, document extraction, UI analysis, and diagram interpretation. Effective multimodal prompting requires combining clear textual instructions with properly structured visual context.

## Sending Images with Prompts

### Claude API

```python
import anthropic
import base64

client = anthropic.Anthropic()

with open("screenshot.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data
                }
            },
            {
                "type": "text",
                "text": "Extract all form field labels and their current values from this screenshot."
            }
        ]
    }]
)
```

### OpenAI API

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_data}"}
            },
            {
                "type": "text",
                "text": "Extract all form field labels and their current values."
            }
        ]
    }]
)
```

## Core Techniques

### Contextual Prompting

Provide context about what the image represents and what you need from it. Without context, models produce generic descriptions:

```text
Without context:
"Describe this image."
-> Generic description of colors, shapes, and objects.

With context:
"This is a screenshot of a React component rendering a data table.
Identify any layout issues: overlapping text, misaligned columns,
or truncated content."
-> Focused analysis of specific UI problems.
```

### Clear Action Verbs

Use directive verbs that define the task explicitly:

| Verb     | Task Type                                  |
| -------- | ------------------------------------------ |
| Extract  | Pull structured data from the image        |
| Compare  | Analyze differences between images         |
| Identify | Find specific elements or patterns         |
| Evaluate | Assess quality, correctness, or compliance |
| Describe | Provide detailed narrative of contents     |
| Count    | Enumerate specific objects or elements     |

```text
"Identify all navigation elements in this wireframe and list them
with their hierarchical relationships."
```

### Multi-Image Prompting

When providing multiple images, clearly label each and specify the relationship:

```text
Image 1: Current design mockup
Image 2: Updated design mockup

Compare these two designs and list all visual differences,
organized by: layout changes, color changes, typography changes,
and added/removed elements.
```

### Chain-of-Thought with Images

Apply CoT reasoning to visual tasks by asking the model to break down its analysis:

```text
Analyze this architecture diagram step by step:
1. Identify all services and their roles
2. Trace the data flow from client request to response
3. Identify potential single points of failure
4. Suggest improvements for high availability
```

## Common Tasks

### Document Extraction

```text
Extract all text from this invoice image into structured JSON with
these fields: vendor_name, invoice_number, date, line_items (array
of {description, quantity, unit_price, total}), subtotal, tax, total.

If any field is unclear or partially obscured, set its value to null
and add a "confidence" field set to "low".
```

### UI Testing and Analysis

```text
This is a screenshot of our checkout page on a 375px mobile viewport.
Evaluate:
1. Are all interactive elements at least 44x44px tap targets?
2. Is text readable without zooming (minimum 16px equivalent)?
3. Are form labels visible and associated with their inputs?
4. Is the primary CTA button visible without scrolling?
```

### Code from Diagrams

```text
This is a UML class diagram. Generate TypeScript interfaces that
match the classes, properties, types, and relationships shown.
Use readonly for properties marked with a lock icon. Implement
inheritance relationships with extends.
```

### Chart and Graph Analysis

```text
Analyze this bar chart and provide:
1. The exact values for each bar (estimate if axis labels are unclear)
2. The trend direction (increasing, decreasing, stable)
3. Any outliers that deviate significantly from the pattern
4. A one-sentence summary of what this data shows
```

## Image Optimization Tips

- **Resolution**: Higher resolution images produce better results but use more tokens. Resize large images to the relevant area when possible.
- **Cropping**: Crop images to the region of interest. A focused crop of a UI element outperforms a full-page screenshot for targeted analysis.
- **Annotations**: For complex images, consider adding numbered markers or bounding boxes to reference specific regions in your prompt.
- **Multiple views**: When analyzing 3D objects or complex layouts, provide multiple angles or zoomed views.

### Crop Tool Pattern

Giving Claude a crop tool to "zoom in" on regions of interest produces consistent quality improvements on image evaluation tasks:

```python
crop_tool = {
    "name": "crop_image",
    "description": "Crop a region of the image for closer inspection.",
    "input_schema": {
        "type": "object",
        "properties": {
            "x": {"type": "integer", "description": "Left coordinate"},
            "y": {"type": "integer", "description": "Top coordinate"},
            "width": {"type": "integer"},
            "height": {"type": "integer"}
        },
        "required": ["x", "y", "width", "height"]
    }
}
```

## Best Practices

1. Always provide context about what the image represents and what analysis you need
2. Use specific action verbs rather than vague instructions like "describe"
3. Label multiple images clearly and specify their relationship
4. Crop images to the region of interest to reduce token usage and improve focus
5. Request structured output (JSON, tables) for extraction tasks
6. Include fallback instructions for unclear or partially obscured content
7. Combine CoT reasoning with visual analysis for complex diagrams
8. Use the crop tool pattern to let models zoom into relevant image regions
