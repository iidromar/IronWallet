import uuid

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import PAYMENT_GATEWAY_URL, SERVICE_BASE_URL
from resources.wallets import wallet_dal as dal
from resources.wallets.wallet_model import FundRequestStatus, SourceType
from resources.wallets.wallet_schema import FundTransferRequest, TopUpRequest, WalletCreate


def create_wallet(db: Session, payload: WalletCreate):
    return dal.create_wallet(db, payload.user_id, payload.currency)


def get_wallet(db: Session, wallet_id: uuid.UUID):
    w = dal.get_wallet(db, wallet_id)
    if not w:
        raise HTTPException(404, "Wallet not found")
    return w


def get_by_iban(db: Session, iban: str):
    w = dal.get_wallet_by_iban(db, iban)
    if not w:
        raise HTTPException(404, "Wallet not found")
    return w


def get_by_user(db: Session, user_id: str):
    w = dal.get_wallet_by_user_id(db, user_id)
    if not w:
        raise HTTPException(404, "Wallet not found")
    return w


def initiate_top_up(db: Session, wallet_id: uuid.UUID, payload: TopUpRequest):
    wallet = dal.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(404, "Wallet not found")

    req = dal.get_or_create_fund_request(
        db=db,
        wallet_id=wallet_id,
        amount=payload.amount,
        currency=payload.currency,
        idempotency_key=payload.idempotency_key,
        source_type=SourceType.top_up,
    )

    if req.status == FundRequestStatus.paid or req.payment_reference:
        return req

    settle_url = f"{SERVICE_BASE_URL}/wallets/{wallet_id}/fundRequests/{req.fund_request_id}/settle"

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"{PAYMENT_GATEWAY_URL}/payments",
                json={
                    "fund_request_id": str(req.fund_request_id),
                    "wallet_id": str(wallet_id),
                    "amount": str(payload.amount),
                    "currency": payload.currency,
                    "idempotency_key": payload.idempotency_key,
                    "settle_callback_url": settle_url,
                },
            )
            resp.raise_for_status()
            req.payment_reference = resp.json().get("payment_id")
            db.commit()
            db.refresh(req)
    except httpx.HTTPStatusError as e:
        raise HTTPException(502, e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(503, str(e))

    return req


def settle_top_up(db: Session, wallet_id: uuid.UUID, fund_request_id: uuid.UUID, reference: str):
    wallet = dal.get_wallet_locked(db, wallet_id)
    if not wallet:
        raise HTTPException(404, "Wallet not found")

    req = dal.get_fund_request(db, fund_request_id)
    if not req:
        raise HTTPException(404, "Fund request not found")

    if str(req.wallet_id) != str(wallet_id):
        raise HTTPException(400, "Fund request does not belong to wallet")

    return dal.settle_fund_request(db, req, wallet, reference)


def process_fund_transfer(db: Session, wallet_id: uuid.UUID, payload: FundTransferRequest):
    wallet = dal.get_wallet_locked(db, wallet_id)
    if not wallet:
        raise HTTPException(404, "Wallet not found")

    req = dal.get_or_create_fund_request(
        db=db,
        wallet_id=wallet_id,
        amount=payload.amount,
        currency=payload.currency,
        idempotency_key=payload.idempotency_key,
        source_type=SourceType.fund_transfer,
    )
    return dal.settle_fund_request(db, req, wallet, payload.reference)


def list_fund_requests(db: Session, wallet_id: uuid.UUID):
    if not dal.get_wallet(db, wallet_id):
        raise HTTPException(404, "Wallet not found")
    return dal.get_fund_requests_for_wallet(db, wallet_id)
