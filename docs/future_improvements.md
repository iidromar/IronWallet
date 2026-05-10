# Future Improvements

## 1. Async Messaging with RabbitMQ

Currently services communicate synchronously over HTTP. If Investment-Wallet is temporarily down when Omnibus tries to settle a transaction, the settlement fails with no automatic recovery.

Introducing RabbitMQ would make inter service communication asynchronous. Messages would be persisted in the broker and retried automatically, making the system resilient to temporary service unavailability. This is particularly important for the settlement flow where money movement must eventually complete.

---

## 2. Caching with Redis

Omnibus currently calls Investment-Wallet on every bank transfer to resolve a virtual IBAN to a wallet ID. Under high volume this creates unnecessary load on Investment-Wallet.

Adding a Redis cache for IBAN lookups (with a short TTL) would reduce this to a single HTTP call per IBAN and serve subsequent requests from memory. The TTL ensures the cache stays fresh if a wallet is ever reassigned or updated.

---

## 3. Authentication and Authorization

The Gateway currently accepts any `X-User-Id` header with no verification. In production:

- **JWT authentication** should be enforced at the Gateway to verify the caller's identity.
- The `userId` claim in the token should be used instead of a plain header.
- Internal services (Investment-Wallet, Payment Gateway, Omnibus) should be on a private network and not publicly accessible (only the Gateway is exposed).
- Service to service calls should use mutual TLS or internal API keys.


