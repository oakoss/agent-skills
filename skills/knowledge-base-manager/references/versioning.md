---
title: Versioning
description: Knowledge versioning strategies including snapshot versioning, event sourcing, and git-style approaches with TypeScript interfaces
tags:
  [knowledge-base, versioning, event-sourcing, audit-trail, rollback, changelog]
---

# Versioning

Knowledge changes over time. Versioning enables audit trails, rollback, and historical queries.

## Snapshot Versioning

Each entry stores its version and link to prior version:

```ts
interface KnowledgeEntry {
  id: string;
  content: string;
  version: number;
  created_at: string;
  updated_at: string;
  updated_by: string;
  changelog: string;
  previous_version?: string;
}
```

## Event Sourcing

Track every change as an immutable event:

```ts
interface KnowledgeEvent {
  event_id: string;
  entity_id: string;
  event_type: 'created' | 'updated' | 'deleted';
  timestamp: string;
  changes: {
    field: string;
    old_value: any;
    new_value: any;
  }[];
  author: string;
}
```

Reconstruct any point-in-time state by replaying events.

## Git-Style Versioning

Treat knowledge like code:

- Commit-based changes with messages
- Branch for experimental knowledge
- Merge when validated
- Pull request-style review for changes

Best for teams familiar with git workflows.

## Choosing a Strategy

| Strategy       | Best For                                   | Complexity |
| -------------- | ------------------------------------------ | ---------- |
| Snapshot       | Simple KB, few updates                     | Low        |
| Event sourcing | High-frequency updates, audit requirements | Medium     |
| Git-style      | Team collaboration, review processes       | High       |
