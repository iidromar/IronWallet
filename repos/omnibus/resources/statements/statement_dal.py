from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from resources.statements.statement_model import Statement, StatementStatus, TransactionType


def get_or_create_statement(db: Session, wallet_id, amount, currency, reference, transaction_type, virtual_iban=None, fund_request_id=None):
    existing = db.execute(
        select(Statement).where(Statement.reference == reference)
    ).scalar_one_or_none()
    if existing:
        return existing

    stmt = Statement(
        wallet_id=wallet_id,
        amount=amount,
        currency=currency,
        reference=reference,
        transaction_type=transaction_type,
        virtual_iban=virtual_iban,
        fund_request_id=fund_request_id,
    )
    db.add(stmt)
    db.commit()
    db.refresh(stmt)
    return stmt


def mark_reconciled(db: Session, stmt: Statement):
    if stmt.status == StatementStatus.reconciled:
        return stmt
    stmt.status = StatementStatus.reconciled
    stmt.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(stmt)
    return stmt


def list_statements(db: Session, wallet_id: Optional[str] = None):
    query = select(Statement).order_by(Statement.created_at.desc())
    if wallet_id:
        query = query.where(Statement.wallet_id == wallet_id)
    return db.execute(query).scalars().all()
