import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from resources.wallets.wallet_model import FundRequest, FundRequestStatus, SourceType, Wallet


def generate_virtual_iban(wallet_id):
    hex_id = str(wallet_id).replace("-", "")[:18].upper()
    return f"SA00IRON{hex_id}"


def create_wallet(db: Session, user_id: str, currency: str):
    w = Wallet(user_id=user_id, currency=currency)
    w.virtual_iban = generate_virtual_iban(w.wallet_id)
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def get_wallet(db: Session, wallet_id: uuid.UUID):
    return db.get(Wallet, wallet_id)


def get_wallet_by_iban(db: Session, iban: str):
    return db.execute(select(Wallet).where(Wallet.virtual_iban == iban)).scalar_one_or_none()


def get_wallet_by_user_id(db: Session, user_id: str):
    return db.execute(select(Wallet).where(Wallet.user_id == user_id)).scalar_one_or_none()


def get_wallet_locked(db: Session, wallet_id: uuid.UUID):
    return db.execute(
        select(Wallet).where(Wallet.wallet_id == wallet_id).with_for_update()
    ).scalar_one_or_none()


def get_or_create_fund_request(db: Session, wallet_id, amount, currency, idempotency_key, source_type):
    existing = db.execute(
        select(FundRequest).where(FundRequest.idempotency_key == idempotency_key)
    ).scalar_one_or_none()
    if existing:
        return existing

    req = FundRequest(
        wallet_id=wallet_id,
        amount=amount,
        currency=currency,
        idempotency_key=idempotency_key,
        source_type=source_type,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_fund_request(db: Session, fund_request_id: uuid.UUID):
    return db.get(FundRequest, fund_request_id)


def get_fund_requests_for_wallet(db: Session, wallet_id: uuid.UUID):
    return (
        db.execute(
            select(FundRequest)
            .where(FundRequest.wallet_id == wallet_id)
            .order_by(FundRequest.created_at.desc())
        )
        .scalars()
        .all()
    )


def settle_fund_request(db: Session, req: FundRequest, wallet: Wallet, reference: str):
    if req.status == FundRequestStatus.paid:
        return req

    wallet.balance += req.amount
    wallet.updated_at = datetime.utcnow()
    req.status = FundRequestStatus.paid
    req.payment_reference = reference
    req.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(req)
    return req
