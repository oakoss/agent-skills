---
title: Templates
description: SVG templates for social media profile images, social media posts, and business cards as React components
tags: [templates, social-media, business-card, svg, react-components]
---

# Templates

## Social Media Profile Image

```typescript
export function SocialProfileImage() {
  return (
    <svg width="400" height="400" viewBox="0 0 400 400">
      <rect width="400" height="400" fill="#0066CC" />
      <circle cx="200" cy="200" r="120" fill="white" />
      <path
        d="M160 200 L240 160 L240 240 Z"
        fill="#0066CC"
      />
    </svg>
  )
}
```

## Social Media Post (1200x630)

```typescript
interface SocialPostProps {
  title: string
  description: string
  imageUrl?: string
}

export function SocialPost({ title, description, imageUrl }: SocialPostProps) {
  return (
    <svg width="1200" height="630" viewBox="0 0 1200 630">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#0066CC" />
          <stop offset="100%" stopColor="#003D7A" />
        </linearGradient>
      </defs>
      <rect width="1200" height="630" fill="url(#bg)" />
      <text
        x="60"
        y="200"
        fontSize="60"
        fontWeight="700"
        fill="white"
        fontFamily="Inter"
      >
        {title}
      </text>
      <text
        x="60"
        y="270"
        fontSize="32"
        fill="#CCE0FF"
        fontFamily="Inter"
      >
        {description}
      </text>
    </svg>
  )
}
```

## Business Card (350x200)

```typescript
interface BusinessCardProps {
  name: string
  title: string
  email: string
  phone: string
}

export function BusinessCard({ name, title, email, phone }: BusinessCardProps) {
  return (
    <svg width="350" height="200" viewBox="0 0 350 200">
      <rect width="350" height="200" fill="white" />
      <text x="20" y="120" fontSize="20" fontWeight="700" fill="#111827">
        {name}
      </text>
      <text x="20" y="145" fontSize="14" fill="#6B7280">
        {title}
      </text>
      <text x="20" y="170" fontSize="12" fill="#6B7280">
        {email}
      </text>
      <text x="20" y="185" fontSize="12" fill="#6B7280">
        {phone}
      </text>
    </svg>
  )
}
```
