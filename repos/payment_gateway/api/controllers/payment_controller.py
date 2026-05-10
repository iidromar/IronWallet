import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from resources.payments.payment_schema import MoyasarWebhookPayload, PaymentCreate, PaymentResponse
from resources.payments.payment_service import create_payment, get_payment, handle_webhook

router = APIRouter()


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create(payload: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment(db, payload)


@router.post("/webhook")
def webhook(payload: MoyasarWebhookPayload, db: Session = Depends(get_db)):
    return handle_webhook(db, payload)


@router.get("/{payment_id}", response_model=PaymentResponse)
def fetch(payment_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_payment(db, payment_id)
