from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from resources.statements.statement_schema import BankTransferWebhook, PaymentSettlementWebhook, StatementResponse
from resources.statements.statement_service import process_bank_transfer, process_payment_settlement

router = APIRouter()


@router.post("/paymentSettlement", response_model=StatementResponse)
def payment_settlement(payload: PaymentSettlementWebhook, db: Session = Depends(get_db)):
    return process_payment_settlement(db, payload)


@router.post("/bankTransfer", response_model=StatementResponse)
def bank_transfer(payload: BankTransferWebhook, db: Session = Depends(get_db)):
    return process_bank_transfer(db, payload)
