---
title: AI Stream Orchestration
description: Token-by-token LLM stream rendering, batching strategies, backpressure handling, and multi-modal stream patterns
tags: [ai-streaming, llm, tokens, backpressure, batching, react, useTransition]
---

# AI Stream Orchestration

Handling live LLM token streams in real-time UIs requires careful rendering strategies to prevent jitter, dropped frames, and memory pressure.

## Token-by-Token Rendering

Subscribe to a real-time channel and batch token updates using `requestAnimationFrame`:

```tsx
import { useState, useEffect, useCallback } from 'react';

function LiveAIResponse({ channelId }: { channelId: string }) {
  const [tokens, setTokens] = useState('');

  useEffect(() => {
    const channel = ably.channels.get(channelId);
    let buffer = '';
    let rafId: number;

    function flush() {
      if (buffer) {
        setTokens((prev) => prev + buffer);
        buffer = '';
      }
      rafId = requestAnimationFrame(flush);
    }

    rafId = requestAnimationFrame(flush);

    channel.subscribe('token', (msg) => {
      buffer += msg.data;
    });

    return () => {
      cancelAnimationFrame(rafId);
      channel.unsubscribe();
    };
  }, [channelId]);

  return <div className="whitespace-pre-wrap">{tokens}</div>;
}
```

The buffer collects tokens between animation frames, then flushes them in a single state update. This prevents one re-render per token.

## useTransition for Non-Blocking Updates

For streams that update complex UI (syntax highlighting, markdown rendering), defer non-urgent updates:

```tsx
import { useState, useTransition, useEffect } from 'react';

function AICodeResponse({ channelId }: { channelId: string }) {
  const [rawTokens, setRawTokens] = useState('');
  const [renderedContent, setRenderedContent] = useState('');
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    const channel = ably.channels.get(channelId);

    channel.subscribe('token', (msg) => {
      setRawTokens((prev) => {
        const next = prev + msg.data;
        startTransition(() => {
          setRenderedContent(highlightSyntax(next));
        });
        return next;
      });
    });

    return () => channel.unsubscribe();
  }, [channelId]);

  return (
    <div>
      <pre>{renderedContent}</pre>
      {isPending ? (
        <span className="text-muted-foreground">Processing...</span>
      ) : null}
    </div>
  );
}
```

`startTransition` marks the syntax highlighting as non-urgent, allowing the raw token accumulation to proceed without blocking.

## Backpressure Handling

When token production outpaces rendering, apply backpressure:

```ts
const MAX_BUFFER_SIZE = 10000;

function createTokenBuffer(onFlush: (tokens: string) => void) {
  let buffer = '';
  let rafId: number;

  function flush() {
    if (buffer) {
      onFlush(buffer);
      buffer = '';
    }
    rafId = requestAnimationFrame(flush);
  }

  rafId = requestAnimationFrame(flush);

  return {
    push(token: string) {
      buffer += token;
      if (buffer.length > MAX_BUFFER_SIZE) {
        cancelAnimationFrame(rafId);
        onFlush(buffer);
        buffer = '';
        rafId = requestAnimationFrame(flush);
      }
    },
    destroy() {
      cancelAnimationFrame(rafId);
    },
  };
}
```

When the buffer exceeds the threshold, force an immediate flush to prevent memory buildup.

## Multi-Stream Orchestration

Handle multiple concurrent AI responses (e.g., parallel tool calls):

```tsx
import { useState, useEffect } from 'react';

type StreamState = {
  id: string;
  tokens: string;
  status: 'streaming' | 'complete' | 'error';
};

function MultiStreamView({ streamIds }: { streamIds: string[] }) {
  const [streams, setStreams] = useState<Map<string, StreamState>>(new Map());

  useEffect(() => {
    const channels = streamIds.map((id) => {
      const channel = ably.channels.get(`ai-stream-${id}`);

      channel.subscribe('token', (msg) => {
        setStreams((prev) => {
          const next = new Map(prev);
          const current = next.get(id) ?? {
            id,
            tokens: '',
            status: 'streaming' as const,
          };
          next.set(id, { ...current, tokens: current.tokens + msg.data });
          return next;
        });
      });

      channel.subscribe('done', () => {
        setStreams((prev) => {
          const next = new Map(prev);
          const current = next.get(id);
          if (current) next.set(id, { ...current, status: 'complete' });
          return next;
        });
      });

      return channel;
    });

    return () => channels.forEach((ch) => ch.unsubscribe());
  }, [streamIds]);

  return (
    <div className="space-y-4">
      {Array.from(streams.values()).map((stream) => (
        <div key={stream.id}>
          <pre>{stream.tokens}</pre>
          {stream.status === 'streaming' ? <span>Streaming...</span> : null}
        </div>
      ))}
    </div>
  );
}
```

## Stream Lifecycle

| Phase     | Action                                             |
| --------- | -------------------------------------------------- |
| Start     | Subscribe to channel, initialize buffer            |
| Streaming | Batch tokens with `requestAnimationFrame`          |
| Complete  | Flush remaining buffer, render final state         |
| Error     | Display error state, offer retry                   |
| Cleanup   | Unsubscribe, cancel animation frames, clear buffer |

## Performance Guidelines

| Metric                      | Target                            |
| --------------------------- | --------------------------------- |
| Re-renders per second       | < 60 (one per animation frame)    |
| Token buffer flush interval | Every animation frame (~16ms)     |
| Memory per stream           | < 1MB for standard text responses |
| Concurrent streams          | Test up to 5 parallel streams     |
