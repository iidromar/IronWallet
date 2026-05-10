# Edge Cases

## 1. Duplicate Top Up Request

**How it's handled:** The `idempotency_key` is unique in the `fund_requests` table. The second request returns the existing fund request without creating a new payment. The client receives the same response both times.

---

## 2. Moyasar Webhook Fires Twice

**How it's handled:**
- In Payment Gateway, `mark_captured` checks if the payment is already captured and returns early if so.
- In Omnibus, `process_payment_settlement` checks if the statement is already reconciled and returns early.
- In Investment-Wallet, `settle_fund_request` checks if the fund request is already paid and returns early.

---

## 3. Concurrent Top-Ups on the Same Wallet

**How it's handled:** `settle_top_up` locks the wallet row with `SELECT FOR UPDATE` before reading and updating the balance. The second transaction blocks at the lock and only proceeds after the first commits, ensuring both amounts are correctly credited.

---

## 4. Delayed Bank Transfer

**How it's handled:** The system is stateless with respect to timing. It processes the transfer whenever the webhook arrives. The `reference` field from the bank serves as the idempotency key in the `statements` table, so even if the notification arrives multiple times it is only processed once.

---

## 5. Payment Gateway is Down During Top Up

**How it's handled:** The fund request remains in `pending` state with no `payment_reference`. The client receives a 502/503 error. They can retry with the same `idempotency_key`, the existing pending fund request is returned and the payment creation is attempted again.

---

## 6. Omnibus Cannot Find Wallet by IBAN

**How it's handled:** Omnibus calls Investment-Wallet's `/wallets/byIban/{iban}` endpoint. If the wallet is not found (404), Omnibus returns a 404 to the caller. No statement is created and no balance is updated.

---

## 7. Investment-Wallet is Down During Settlement

**How it's handled:** The statement is not marked as reconciled. If Payment Gateway retries the webhook (or an operator replays it), Omnibus will see the statement is still pending and attempt the callback again. In production this would be handled by a retry queue (see [Future Improvements](./future_improvements.md)).

---

## 8. Conflicting Fund Requests with Same Idempotency Key

**How it's handled:** The first request wins. The second request returns the existing fund request regardless of the amount in the new request. 
