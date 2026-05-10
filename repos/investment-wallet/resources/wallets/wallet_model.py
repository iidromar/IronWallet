import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from db.models.model_base import Base


class FundRequestStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    paid = "paid"
    failed = "failed"


class SourceType(str, enum.Enum):
    top_up = "top_up"
    fund_transfer = "fund_transfer"


class Wallet(Base):
    __tablename__ = "wallets"

    wallet_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(128), nullable=False, unique=True, index=True)
    balance = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="SAR")
    virtual_iban = Column(String(34), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class FundRequest(Base):
    __tablename__ = "fund_requests"

    fund_request_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(
        UUID(as_uuid=True), ForeignKey("wallets.wallet_id"), nullable=False, index=True
    )
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency = Column(String(3), nullable=False, default="SAR")
    status = Column(
        Enum(FundRequestStatus, native_enum=False),
        nullable=False,
        default=FundRequestStatus.pending,
    )
    idempotency_key = Column(String(255), nullable=False, unique=True, index=True)
    source_type = Column(Enum(SourceType, native_enum=False), nullable=False)
    payment_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
