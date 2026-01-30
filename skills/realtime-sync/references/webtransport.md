---
title: WebTransport Streaming
description: WebTransport bidirectional streams, datagrams, Web Worker patterns, congestion control, and fallback strategies
tags: [webtransport, http3, streams, datagrams, fallback]
---

# WebTransport Streaming

WebTransport is the HTTP/3-powered replacement for WebSockets. It supports multiple streams within a single connection and both reliable and unreliable data delivery.

## Stream Types

| Type                  | Delivery              | Use Case                                    |
| --------------------- | --------------------- | ------------------------------------------- |
| Bidirectional stream  | Reliable, ordered     | Request-response, handshakes                |
| Unidirectional stream | Reliable, ordered     | One-way state pushes                        |
| Datagrams             | Unreliable, unordered | High-frequency game state, cursor positions |

## Basic Client Connection

```ts
const transport = new WebTransport('https://example.com/api/realtime');
await transport.ready;

const stream = await transport.createBidirectionalStream();
const writer = stream.writable.getWriter();
const reader = stream.readable.getReader();

await writer.write(new TextEncoder().encode(JSON.stringify({ type: 'join' })));

const { value } = await reader.read();
const response = JSON.parse(new TextDecoder().decode(value));
```

## Datagram Channel (Unreliable/Fast)

For high-frequency updates where losing a frame is better than waiting for retransmission:

```ts
const transport = new WebTransport(serverUrl);
await transport.ready;

const datagramWriter = transport.datagrams.writable.getWriter();

function sendCursorPosition(x: number, y: number) {
  const payload = new Float32Array([x, y]);
  datagramWriter.write(new Uint8Array(payload.buffer));
}

async function readDatagrams() {
  const reader = transport.datagrams.readable.getReader();
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    const coords = new Float32Array(value.buffer);
    updateRemoteCursor(coords[0], coords[1]);
  }
}
```

## Web Worker Pattern

Handle WebTransport inside a Web Worker to prevent blocking the UI thread:

```ts
// transport.worker.ts
const transport = new WebTransport(url);
await transport.ready;

const stream = await transport.createUnidirectionalStream();
const writer = stream.writable.getWriter();

self.onmessage = ({ data }) => {
  writer.write(new TextEncoder().encode(JSON.stringify(data)));
};
```

```ts
// main thread
const worker = new Worker(new URL('./transport.worker.ts', import.meta.url), {
  type: 'module',
});

worker.postMessage({ type: 'cursor', x: 100, y: 200 });
```

## Congestion Control

WebTransport uses BBR v3 for congestion control. Monitor connection health:

```ts
const stats = await transport.getStats();
console.log('RTT:', stats.rtt);
console.log('Bytes sent:', stats.bytesSent);
console.log('Packets lost:', stats.packetsLost);
```

High packet loss indicates network saturation. Reduce send frequency or switch to reliable streams.

## WebSocket Fallback

Enterprise firewalls may block UDP (HTTP/3). Implement a detection and fallback:

```ts
async function createTransport(url: string) {
  if ('WebTransport' in globalThis) {
    try {
      const transport = new WebTransport(url);
      await transport.ready;
      return { type: 'webtransport' as const, transport };
    } catch {
      // WebTransport blocked or failed
    }
  }

  const ws = new WebSocket(url.replace('https:', 'wss:'));
  return new Promise<{ type: 'websocket'; transport: WebSocket }>((resolve) => {
    ws.onopen = () => resolve({ type: 'websocket', transport: ws });
  });
}
```

## Common Pitfalls

| Issue                | Cause                                                     | Fix                                        |
| -------------------- | --------------------------------------------------------- | ------------------------------------------ |
| Certificate errors   | WebTransport requires hash-based auth without standard CA | Use standard CA certificates in production |
| Stream leaks         | Streams not closed on component unmount                   | Close all streams in cleanup/teardown      |
| Firewall blocking    | Enterprise networks block UDP                             | Implement WebSocket fallback               |
| Black hole detection | Server unreachable but no error                           | Monitor `transport.closed` promise         |

## Stream Lifecycle

Always clean up streams when they are no longer needed:

```ts
async function cleanup(transport: WebTransport) {
  try {
    transport.close({ closeCode: 0, reason: 'Client disconnecting' });
  } catch {
    // Transport may already be closed
  }
  await transport.closed;
}
```
