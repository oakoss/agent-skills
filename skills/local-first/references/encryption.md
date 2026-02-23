---
title: Encryption
description: End-to-end encryption for synced local-first data including Web Crypto API, key management, and E2EE with CRDTs
tags:
  [
    e2ee,
    encryption,
    web-crypto,
    aes-gcm,
    key-exchange,
    crdt,
    libsodium,
    security,
  ]
---

## Web Crypto API Pattern

AES-GCM-256 provides authenticated encryption with built-in tamper detection. The Web Crypto API is available in all modern browsers and requires no dependencies.

### Key Generation

```ts
async function generateEncryptionKey(): Promise<CryptoKey> {
  return crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, [
    'encrypt',
    'decrypt',
  ]);
}

async function exportKey(key: CryptoKey): Promise<ArrayBuffer> {
  return crypto.subtle.exportKey('raw', key);
}

async function importKey(raw: ArrayBuffer): Promise<CryptoKey> {
  return crypto.subtle.importKey('raw', raw, { name: 'AES-GCM' }, true, [
    'encrypt',
    'decrypt',
  ]);
}
```

### Encrypt and Decrypt

```ts
async function encrypt(
  key: CryptoKey,
  plaintext: Uint8Array,
): Promise<{ iv: Uint8Array; ciphertext: ArrayBuffer }> {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    plaintext,
  );
  return { iv, ciphertext };
}

async function decrypt(
  key: CryptoKey,
  iv: Uint8Array,
  ciphertext: ArrayBuffer,
): Promise<ArrayBuffer> {
  return crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, ciphertext);
}
```

## Multi-User Key Management

Each document gets a symmetric key for content encryption. Asymmetric key exchange distributes the document key to authorized users.

### Per-Document Key with Asymmetric Exchange

```ts
async function generateKeyPair(): Promise<CryptoKeyPair> {
  return crypto.subtle.generateKey(
    {
      name: 'RSA-OAEP',
      modulusLength: 4096,
      publicExponent: new Uint8Array([1, 0, 1]),
      hash: 'SHA-256',
    },
    true,
    ['wrapKey', 'unwrapKey'],
  );
}

async function wrapDocumentKey(
  documentKey: CryptoKey,
  recipientPublicKey: CryptoKey,
): Promise<ArrayBuffer> {
  return crypto.subtle.wrapKey('raw', documentKey, recipientPublicKey, {
    name: 'RSA-OAEP',
  });
}

async function unwrapDocumentKey(
  wrappedKey: ArrayBuffer,
  privateKey: CryptoKey,
): Promise<CryptoKey> {
  return crypto.subtle.unwrapKey(
    'raw',
    wrappedKey,
    privateKey,
    { name: 'RSA-OAEP' },
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt', 'decrypt'],
  );
}
```

### Key Distribution Flow

```text
1. Creator generates AES-GCM-256 document key
2. Creator wraps document key with each collaborator's RSA public key
3. Wrapped keys stored alongside document metadata (unencrypted envelope)
4. Each collaborator unwraps with their RSA private key
5. On member removal: rotate document key + re-wrap for remaining members
```

## Encryption Approaches

### Symmetric + Asymmetric Hybrid

The standard web approach. AES-GCM for content, RSA-OAEP or ECDH for key exchange. Works with Web Crypto API directly. Best for: client-server architectures where a server can broker key exchange.

### MLS (RFC 9420 — Messaging Layer Security)

Group key agreement protocol designed for large groups. Provides forward secrecy and post-compromise security. Members share a group secret via a ratchet tree — adding/removing members is O(log n). Best for: large collaborative groups where membership changes frequently.

### Keyhive (P2P)

Capability-based key management for peer-to-peer systems. No central server required. Keys are distributed through a directed acyclic graph of capabilities. Built for local-first architectures where devices sync directly. Best for: fully decentralized apps without a central authority.

## E2EE with CRDTs

Encrypting CRDT updates requires care — the CRDT layer must see plaintext to merge, but the transport layer must only see ciphertext.

### SecSync (Yjs + XChaCha20-Poly1305)

```ts
import { createSyncEngine } from 'secsync';

const engine = createSyncEngine({
  documentId: 'doc-123',
  signatureKeyPair: userSignatureKeys,
  websocketEndpoint: 'wss://sync.example.com',
  sodium,
  getDocumentKey: async () => documentSymmetricKey,
  getYDoc: () => yDoc,
});
```

SecSync encrypts each Yjs update before sending to the server. The server stores opaque ciphertext and routes it to peers. Server never sees plaintext content.

### Jazz (CRDT + Crypto Permissions)

Jazz combines CRDTs with a built-in permission system. Each CoValue (collaborative value) has an owner group with role-based access. Encryption keys are derived from group membership. The framework handles key rotation on membership changes automatically.

### @localfirst/crdx

Provides encrypted CRDT synchronization with a hash graph structure. Each change is signed by its author and encrypted for the group. Supports fine-grained permissions at the field level.

## Architecture Pattern

```text
┌─────────────┐     encrypt      ┌─────────────┐     network      ┌─────────────┐
│  CRDT Layer │ ──────────────▶  │  Encrypted   │ ──────────────▶  │   Server    │
│ (plaintext) │                  │   Updates    │                  │ (ciphertext)│
└─────────────┘     decrypt      └─────────────┘     network      └─────────────┘
       ▲         ◀──────────────         ▲         ◀──────────────        │
       │                                 │                                │
       └─── merge locally ───────────────┘                                │
                                                                          │
                                         routes to other peers ───────────┘
```

Metadata (document ID, sender ID, timestamps) stays unencrypted so the server can route updates without decrypting content.

### Encrypt-Before-Send Pattern

```ts
async function encryptUpdate(
  key: CryptoKey,
  update: Uint8Array,
): Promise<Uint8Array> {
  const { iv, ciphertext } = await encrypt(key, update);
  const combined = new Uint8Array(iv.length + ciphertext.byteLength);
  combined.set(iv);
  combined.set(new Uint8Array(ciphertext), iv.length);
  return combined;
}

async function decryptUpdate(
  key: CryptoKey,
  payload: Uint8Array,
): Promise<Uint8Array> {
  const iv = payload.slice(0, 12);
  const ciphertext = payload.slice(12);
  const plaintext = await decrypt(key, iv, ciphertext.buffer);
  return new Uint8Array(plaintext);
}
```

## Libraries

| Library          | Type        | Size    | Notes                                      |
| ---------------- | ----------- | ------- | ------------------------------------------ |
| Web Crypto API   | Built-in    | 0 KB    | AES-GCM, RSA-OAEP, ECDH. All browsers.     |
| libsodium.js     | WASM        | ~180 KB | XChaCha20-Poly1305, Ed25519, X25519        |
| sodium-plus      | Wrapper     | ~10 KB  | Ergonomic API over libsodium.js            |
| vodozemac        | Rust → WASM | ~150 KB | Olm/Megolm (Matrix protocol encryption)    |
| SecSync          | Framework   | Varies  | Yjs + XChaCha20-Poly1305 integration       |
| Jazz             | Framework   | Varies  | Built-in CRDT encryption + permissions     |
| @localfirst/crdx | Framework   | Varies  | Hash graph CRDT with per-change encryption |

### When to Use What

- **Simple document encryption**: Web Crypto API (zero dependencies)
- **Group messaging with forward secrecy**: libsodium.js + custom MLS implementation
- **Yjs-based collaboration**: SecSync
- **Full-stack local-first with permissions**: Jazz
- **P2P without central authority**: @localfirst/crdx with Keyhive
