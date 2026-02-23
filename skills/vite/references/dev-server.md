---
title: Dev Server
description: Vite dev server configuration including proxy, HMR, HTTPS, middleware, and file watching
tags: [server, proxy, hmr, https, middleware, watch, cors, open, host]
---

# Dev Server

## Basic Server Config

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3000,
    strictPort: true,
    host: '0.0.0.0',
    open: true,
    cors: true,
  },
});
```

| Option       | Default       | Purpose                                         |
| ------------ | ------------- | ----------------------------------------------- |
| `port`       | `5173`        | Dev server port                                 |
| `strictPort` | `false`       | Fail if port is in use (instead of trying next) |
| `host`       | `'localhost'` | Set `'0.0.0.0'` or `true` to expose on network  |
| `open`       | `false`       | Open browser on start; can be a URL string      |
| `cors`       | `false`       | Enable CORS headers                             |

## Proxy Configuration

Forward API requests to a backend server during development:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        secure: false,
      },

      '/api/v2': {
        target: 'http://localhost:9090',
        changeOrigin: true,
      },

      '/socket.io': {
        target: 'ws://localhost:5174',
        ws: true,
        rewriteWsOrigin: true,
      },

      '/foo': 'http://localhost:4567',
    },
  },
});
```

### Proxy Options

| Option         | Purpose                                                     |
| -------------- | ----------------------------------------------------------- |
| `target`       | Backend server URL                                          |
| `changeOrigin` | Set `Host` header to target (needed for virtual hosts)      |
| `rewrite`      | Transform the request path                                  |
| `secure`       | Verify SSL certs (disable for self-signed)                  |
| `ws`           | Enable WebSocket proxying                                   |
| `configure`    | Access underlying `http-proxy` instance for event listeners |

### Advanced Proxy with Event Listeners

```ts
'/api': {
  target: 'http://localhost:8080',
  changeOrigin: true,
  configure: (proxy, options) => {
    proxy.on('proxyReq', (proxyReq, req, res) => {
      proxyReq.setHeader('X-Forwarded-For', req.socket.remoteAddress ?? '')
    })
    proxy.on('error', (err, req, res) => {
      console.error('Proxy error:', err.message)
    })
  },
}
```

### RegExp Path Matching

```ts
'^/api/v[0-9]+/.*': {
  target: 'http://api.example.com',
  changeOrigin: true,
}
```

## HMR Configuration

Customize Hot Module Replacement behavior:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 3000,
      overlay: true,
    },
  },
});
```

| Option       | Purpose                                         |
| ------------ | ----------------------------------------------- |
| `protocol`   | `'ws'` or `'wss'`                               |
| `host`       | WebSocket host (useful behind reverse proxy)    |
| `port`       | WebSocket port                                  |
| `overlay`    | Show error overlay in browser                   |
| `clientPort` | Override port on client side (for proxy setups) |

### HMR Behind a Reverse Proxy

When running behind nginx or similar:

```ts
server: {
  hmr: {
    host: 'my-domain.com',
    clientPort: 443,
    protocol: 'wss',
  },
}
```

### Client-Side HMR API

Modules can self-accept HMR updates to preserve state:

```ts
let count = 0;

export function increment() {
  count++;
  render();
}

if (import.meta.hot) {
  if (import.meta.hot.data.count !== undefined) {
    count = import.meta.hot.data.count;
  }

  import.meta.hot.accept((newModule) => {
    if (newModule) newModule.render();
  });

  import.meta.hot.dispose((data) => {
    data.count = count;
  });
}
```

## HTTPS Dev Server

Enable HTTPS with TLS certificates:

```ts
import { defineConfig } from 'vite';
import { readFileSync } from 'node:fs';

export default defineConfig({
  server: {
    https: {
      key: readFileSync('./certs/localhost-key.pem'),
      cert: readFileSync('./certs/localhost.pem'),
    },
  },
});
```

For local development, generate certs with `mkcert`:

```bash
mkcert -install
mkcert localhost 127.0.0.1 ::1
```

Alternatively, use the `@vitejs/plugin-basic-ssl` plugin for auto-generated untrusted certs:

```ts
import { defineConfig } from 'vite';
import basicSsl from '@vitejs/plugin-basic-ssl';

export default defineConfig({
  plugins: [basicSsl()],
});
```

## File System Watching

Configure the file watcher:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    watch: {
      ignored: ['**/node_modules/**', '**/.git/**'],
      usePolling: true,
      interval: 1000,
    },
  },
});
```

`usePolling` is needed in some environments (Docker, WSL, network filesystems) where native file watching does not work reliably.

## Preview Server

The `vite preview` command serves the production build locally. It shares similar config options under `preview`:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  preview: {
    port: 4173,
    strictPort: true,
    host: '0.0.0.0',
    proxy: {
      '/api': 'http://localhost:8080',
    },
  },
});
```
