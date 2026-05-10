import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from resources.wallets.wallet_schema import (
    FundRequestResponse,
    FundTransferRequest,
    TopUpRequest,
    TopUpSettleRequest,
    WalletCreate,
    WalletResponse,
)
from resources.wallets.wallet_service import (
    create_wallet,
    get_wallet,
    get_by_iban,
    get_by_user,
    initiate_top_up,
    list_fund_requests,
    process_fund_transfer,
    settle_top_up,
)

router = APIRouter()


@router.post("", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
def create(payload: WalletCreate, db: Session = Depends(get_db)):
    return create_wallet(db, payload)


@router.get("/byIban/{virtual_iban}", response_model=WalletResponse)
def by_iban(virtual_iban: str, db: Session = Depends(get_db)):
    return get_by_iban(db, virtual_iban)


@router.get("/byUser/{user_id}", response_model=WalletResponse)
def by_user(user_id: str, db: Session = Depends(get_db)):
    return get_by_user(db, user_id)


@router.get("/{wallet_id}", response_model=WalletResponse)
def fetch(wallet_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_wallet(db, wallet_id)


@router.post("/{wallet_id}/topUp", response_model=FundRequestResponse, status_code=status.HTTP_202_ACCEPTED)
def top_up(wallet_id: uuid.UUID, payload: TopUpRequest, db: Session = Depends(get_db)):
    return initiate_top_up(db, wallet_id, payload)


@router.post("/{wallet_id}/fundRequests/{fund_request_id}/settle", response_model=FundRequestResponse)
def settle(wallet_id: uuid.UUID, fund_request_id: uuid.UUID, payload: TopUpSettleRequest, db: Session = Depends(get_db)):
    return settle_top_up(db, wallet_id, fund_request_id, payload.reference)


@router.post("/{wallet_id}/fundTransfers", response_model=FundRequestResponse, status_code=status.HTTP_201_CREATED)
def fund_transfer(wallet_id: uuid.UUID, payload: FundTransferRequest, db: Session = Depends(get_db)):
    return process_fund_transfer(db, wallet_id, payload)


@router.get("/{wallet_id}/fundRequests", response_model=list[FundRequestResponse])
def fund_requests(wallet_id: uuid.UUID, db: Session = Depends(get_db)):
    return list_fund_requests(db, wallet_id)
