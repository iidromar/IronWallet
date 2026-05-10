from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from resources.statements.statement_model import StatementStatus, TransactionType


class PaymentSettlementWebhook(BaseModel):
    payment_id: str
    fund_request_id: str
    wallet_id: str
    amount: Decimal
    currency: str
    reference: str
    settle_callback_url: str


class BankTransferWebhook(BaseModel):
    virtual_iban: str
    amount: Decimal
    currency: str = "SAR"
    reference: str


class StatementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    statement_id: UUID
    wallet_id: str
    virtual_iban: Optional[str]
    amount: Decimal
    currency: str
    reference: str
    transaction_type: TransactionType
    status: StatementStatus
    fund_request_id: Optional[str]
    created_at: datetime
