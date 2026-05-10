import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from db.models.model_base import Base


class TransactionType(str, enum.Enum):
    top_up = "top_up"
    fund_transfer = "fund_transfer"


class StatementStatus(str, enum.Enum):
    pending = "pending"
    reconciled = "reconciled"


class Statement(Base):
    __tablename__ = "statements"

    statement_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(String(255), nullable=False, index=True)
    virtual_iban = Column(String(34), nullable=True, index=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency = Column(String(3), nullable=False, default="SAR")
    reference = Column(String(255), nullable=False, unique=True, index=True)
    transaction_type = Column(Enum(TransactionType, native_enum=False), nullable=False)
    status = Column(
        Enum(StatementStatus, native_enum=False),
        nullable=False,
        default=StatementStatus.pending,
    )
    fund_request_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
