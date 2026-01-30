---
name: realtime-sync
description: 'Low-latency synchronization with WebTransport, pub/sub messaging, CRDTs, and AI stream orchestration. Covers bidirectional streaming, transactional outbox patterns, sequence tracking, and collaborative editing. Use when building real-time collaborative UIs, implementing pub/sub messaging, handling WebTransport or WebSocket connections, orchestrating live AI token streams, or resolving conflicts with CRDTs.'
---

# Realtime Sync

## Overview

Architects high-concurrency, sub-50ms latency synchronization between distributed clients and servers. Covers WebTransport (HTTP/3) bidirectional streaming, transactional outbox patterns for database-to-sync consistency, CRDTs for collaborative editing, and AI token stream orchestration.

**When to use:** Real-time collaborative UIs, pub/sub messaging, WebTransport/WebSocket connections, live AI token streams, presence tracking, conflict resolution with CRDTs.

**When NOT to use:** Batch processing pipelines, static content delivery, request-response APIs without real-time requirements, offline-only applications.

## Quick Reference

| Pattern              | Approach                                    | Key Points                                               |
| -------------------- | ------------------------------------------- | -------------------------------------------------------- |
| WebTransport         | `new WebTransport(url)` + `await ready`     | HTTP/3 multiplexed; replaces WebSockets for new projects |
| Bidirectional stream | `transport.createBidirectionalStream()`     | Reader/writer pair for request-response loops            |
| Datagrams            | `transport.datagrams.writable`              | UDP-like unreliable delivery for high-frequency state    |
| Transactional outbox | DB write + outbox insert in one transaction | CDC worker pushes to channel; prevents state drift       |
| Sequence tracking    | Sequence IDs on every message               | Rewind on reconnect to fetch missed messages             |
| CRDT collaboration   | Yjs (text) or Automerge (JSON state)        | Conflict-free concurrent editing without locks           |
| Presence             | Heartbeat-based user tracking               | Epidemic broadcast for robust cleanup                    |
| AI stream batching   | `requestAnimationFrame` for token rendering | Prevents UI jitter from high-frequency updates           |
| Buffer-and-batch     | `useTransition` for sync-triggered updates  | Defers non-urgent re-renders during sync bursts          |
| WebSocket fallback   | Detect WebTransport support first           | Enterprise firewalls may block UDP/HTTP/3                |
| Serialization        | Protocol Buffers or MessagePack             | Avoid JSON.stringify on 100Hz+ streams                   |
| Web Worker transport | Handle WebTransport in a Web Worker         | Prevents blocking the UI thread                          |

## Common Mistakes

| Mistake                                                        | Correct Pattern                                                      |
| -------------------------------------------------------------- | -------------------------------------------------------------------- |
| Using real-time messages as the primary source of truth        | State lives in the database; real-time is the notification of change |
| Using JSON.stringify on high-frequency streams (100Hz+)        | Use Protocol Buffers or MessagePack for serialization                |
| Ignoring sequence drift when a client misses messages          | Implement Sequence IDs and a rewind mechanism on the client          |
| Implementing global locks for concurrent access                | Use Optimistic UI and CRDTs for conflict-free collaboration          |
| Sticking with WebSockets for new projects needing multiplexing | Use WebTransport (HTTP/3) for bidirectional, multiplexed streams     |
| CRDT document bloat from unbounded history                     | Use snapshotting (LWW) for fields that do not need history           |
| Failing to close WebTransport streams on unmount               | Explicitly close streams to prevent transport crashes                |

## Delegation

- **Explore transport protocol options and latency benchmarks**: Use `Explore` agent to compare WebTransport, SSE, and WebSocket tradeoffs
- **Implement transactional outbox pattern with CDC pipeline**: Use `Task` agent to set up database triggers, outbox table, and background worker
- **Design real-time architecture for collaborative editing**: Use `Plan` agent to map CRDT strategy, presence management, and conflict resolution flow

## References

- [WebTransport streaming and worker patterns](references/webtransport.md)
- [Pub/sub messaging and guaranteed delivery](references/pubsub-delivery.md)
- [CRDTs and collaborative editing](references/crdt-collaboration.md)
- [AI stream orchestration patterns](references/ai-stream-orchestration.md)
