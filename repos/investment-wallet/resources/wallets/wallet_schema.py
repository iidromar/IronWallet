from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from resources.wallets.wallet_model import FundRequestStatus, SourceType


class WalletCreate(BaseModel):
    user_id: str
    currency: str = "SAR"


class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    wallet_id: UUID
    user_id: str
    balance: Decimal
    currency: str
    virtual_iban: str
    created_at: datetime


class TopUpRequest(BaseModel):
    amount: Decimal
    currency: str = "SAR"
    idempotency_key: str


class TopUpSettleRequest(BaseModel):
    reference: str


class FundTransferRequest(BaseModel):
    amount: Decimal
    currency: str = "SAR"
    idempotency_key: str
    reference: str


class FundRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fund_request_id: UUID
    wallet_id: UUID
    amount: Decimal
    currency: str
    status: FundRequestStatus
    source_type: SourceType
    payment_reference: Optional[str]
    created_at: datetime
