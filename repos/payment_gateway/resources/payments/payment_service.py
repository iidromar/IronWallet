import uuid

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import OMNIBUS_URL
from resources.payments import payment_dal as dal
from resources.payments.payment_schema import MoyasarWebhookPayload, PaymentCreate


def create_payment(db: Session, payload: PaymentCreate):
    return dal.get_or_create_payment(
        db=db,
        fund_request_id=payload.fund_request_id,
        wallet_id=payload.wallet_id,
        amount=payload.amount,
        currency=payload.currency,
        idempotency_key=payload.idempotency_key,
        settle_callback_url=payload.settle_callback_url,
    )


def handle_webhook(db: Session, payload: MoyasarWebhookPayload):
    if payload.status != "paid":
        return {"detail": "ignored"}

    payment = dal.get_payment_by_fund_request(db, payload.fund_request_id)
    if not payment:
        raise HTTPException(404, "Payment not found")

    payment = dal.mark_captured(db, payment, provider_reference=payload.id)

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"{OMNIBUS_URL}/webhooks/paymentSettlement",
                json={
                    "payment_id": str(payment.payment_id),
                    "fund_request_id": payment.fund_request_id,
                    "wallet_id": payment.wallet_id,
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                    "reference": payload.id,
                    "settle_callback_url": payment.settle_callback_url,
                },
            )
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(503, str(e))

    return {"detail": "processed"}


def get_payment(db: Session, payment_id: uuid.UUID):
    p = dal.get_payment(db, payment_id)
    if not p:
        raise HTTPException(404, "Payment not found")
    return p
