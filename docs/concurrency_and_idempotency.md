# Concurrency and Idempotency

## Idempotency

Every operation that modifies state accepts an `idempotency_key` from the caller. This key is stored with a unique constraint in the database. If the same request is sent twice, the second call returns the existing record instead of creating a duplicate.

### How it works

**Fund Requests (Investment-Wallet)**

Before creating a new fund request, the service queries by `idempotency_key`:

```python
existing = db.execute(
    select(FundRequest).where(FundRequest.idempotency_key == idempotency_key)
).scalar_one_or_none()
if existing:
    return existing
```

If an existing record is found it is returned immediately. No double payment is created.

**Payments (Payment Gateway)**

Same pattern — `idempotency_key` is unique in the `payments` table. If Investment-Wallet retries the payment creation (like after a timeout), the same payment record is returned.

**Statements (Omnibus)**

Statements use the provider `reference` as their unique key. If Moyasar fires the same webhook twice, or a bank sends duplicate transfer notifications, the second call hits the already reconciled statement and returns early:

```python
if stmt.status == StatementStatus.reconciled:
    return stmt
```

---

## Concurrency

### The Problem

Two concurrent top up requests for the same wallet could both read the same balance, both add to it and commit, resulting in only one of the amounts actually being reflected. 

### The Solution (SELECT FOR UPDATE)

Before any balance update, the wallet row is locked at the database level:

```python
select(Wallet).where(Wallet.wallet_id == wallet_id).with_for_update()
```

`WITH FOR UPDATE` tells CockroachDB to lock the row for the duration of the transaction. Any other transaction that tries to read the same wallet with a lock will block until the first one commits. This guarantees that balance updates are serialized.

### Where it is applied

- `settle_top_up` : locks wallet before updating balance after a top up settles
- `process_fund_transfer` : locks wallet before crediting a bank transfer amount

### Why not lock on FundRequest creation?

FundRequest creation is guarded by the `idempotency_key` unique constraint, not a row lock. The lock is only needed at the point where money actually moves (balance update). Locking earlier would reduce throughput unnecessarily.

---

## Partial Failure Handling

### Investment-Wallet → Payment Gateway (Top-Up)

If the HTTP call to Payment Gateway fails after the fund request is created, the fund request stays in `pending` state. The client can retry with the same `idempotency_key` and the service will attempt the payment creation again:

```python
if req.status == FundRequestStatus.paid or req.payment_reference:
    return req  
```

### Payment Gateway → Omnibus (Webhook)

If the Omnibus call fails after Payment Gateway marks the payment as captured, the payment is captured in the database but the wallet balance is not yet updated. This is a gap that would be addressed in a production system with a retry queue, see [Future Improvements](./future_improvements.md).

### Omnibus → Investment-Wallet (Settlement Callback)

If the settlement callback to Investment-Wallet fails, the statement is not marked as reconciled. A retry of the same webhook from Payment Gateway will reenter `process_payment_settlement`, see the statement is still pending, and attempt the callback again.
