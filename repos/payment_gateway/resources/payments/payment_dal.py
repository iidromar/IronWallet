import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from resources.payments.payment_model import Payment, PaymentStatus


def get_or_create_payment(db: Session, fund_request_id, wallet_id, amount, currency, idempotency_key, settle_callback_url):
    existing = db.execute(
        select(Payment).where(Payment.idempotency_key == idempotency_key)
    ).scalar_one_or_none()
    if existing:
        return existing

    p = Payment(
        fund_request_id=fund_request_id,
        wallet_id=wallet_id,
        amount=amount,
        currency=currency,
        idempotency_key=idempotency_key,
        settle_callback_url=settle_callback_url,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def get_payment(db: Session, payment_id: uuid.UUID):
    return db.get(Payment, payment_id)


def get_payment_by_fund_request(db: Session, fund_request_id: str):
    return db.execute(
        select(Payment).where(Payment.fund_request_id == fund_request_id)
    ).scalar_one_or_none()


def mark_captured(db: Session, payment: Payment, provider_reference: str):
    if payment.status == PaymentStatus.captured:
        return payment
    payment.status = PaymentStatus.captured
    payment.provider_reference = provider_reference
    db.commit()
    db.refresh(payment)
    return payment
