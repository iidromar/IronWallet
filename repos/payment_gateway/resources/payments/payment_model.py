import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from db.models.model_base import Base


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    captured = "captured"
    failed = "failed"


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fund_request_id = Column(String(255), nullable=False, unique=True, index=True)
    wallet_id = Column(String(255), nullable=False, index=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency = Column(String(3), nullable=False, default="SAR")
    status = Column(
        Enum(PaymentStatus, native_enum=False),
        nullable=False,
        default=PaymentStatus.pending,
    )
    idempotency_key = Column(String(255), nullable=False, unique=True, index=True)
    provider_reference = Column(String(255), nullable=True)
    settle_callback_url = Column(String(512), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
