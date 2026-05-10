from typing import Optional

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import INVESTMENT_WALLET_URL
from resources.statements import statement_dal as dal
from resources.statements.statement_model import StatementStatus, TransactionType
from resources.statements.statement_schema import BankTransferWebhook, PaymentSettlementWebhook


def process_payment_settlement(db: Session, payload: PaymentSettlementWebhook):
    stmt = dal.get_or_create_statement(
        db=db,
        wallet_id=payload.wallet_id,
        amount=payload.amount,
        currency=payload.currency,
        reference=payload.reference,
        transaction_type=TransactionType.top_up,
        fund_request_id=payload.fund_request_id,
    )

    if stmt.status == StatementStatus.reconciled:
        return stmt

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(payload.settle_callback_url, json={"reference": payload.reference})
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(503, str(e))

    return dal.mark_reconciled(db, stmt)


def process_bank_transfer(db: Session, payload: BankTransferWebhook):
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{INVESTMENT_WALLET_URL}/wallets/byIban/{payload.virtual_iban}")
            resp.raise_for_status()
            wallet_data = resp.json()
    except httpx.HTTPStatusError:
        raise HTTPException(404, f"No wallet found for IBAN {payload.virtual_iban}")
    except httpx.RequestError as e:
        raise HTTPException(503, str(e))

    wallet_id = wallet_data["wallet_id"]

    stmt = dal.get_or_create_statement(
        db=db,
        wallet_id=wallet_id,
        amount=payload.amount,
        currency=payload.currency,
        reference=payload.reference,
        transaction_type=TransactionType.fund_transfer,
        virtual_iban=payload.virtual_iban,
    )

    if stmt.status == StatementStatus.reconciled:
        return stmt

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"{INVESTMENT_WALLET_URL}/wallets/{wallet_id}/fundTransfers",
                json={
                    "amount": str(payload.amount),
                    "currency": payload.currency,
                    "idempotency_key": payload.reference,
                    "reference": payload.reference,
                },
            )
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(503, str(e))

    return dal.mark_reconciled(db, stmt)


def list_statements(db: Session, wallet_id: Optional[str] = None):
    return dal.list_statements(db, wallet_id)
