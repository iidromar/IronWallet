from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from resources.payments.payment_model import PaymentStatus


class PaymentCreate(BaseModel):
    fund_request_id: str
    wallet_id: str
    amount: Decimal
    currency: str = "SAR"
    idempotency_key: str
    settle_callback_url: str


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: UUID
    fund_request_id: str
    wallet_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider_reference: Optional[str]
    created_at: datetime


class MoyasarWebhookPayload(BaseModel):
    id: str
    status: str
    fund_request_id: str
    wallet_id: str
